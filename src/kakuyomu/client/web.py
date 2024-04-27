"""
Web client for kakuyomu

This module is a web client for kakuyomu.jp.
"""
import pickle
import time
from typing import Iterable, Sequence

import requests
import toml
from requests.cookies import RequestsCookieJar

from kakuyomu.logger import get_logger
from kakuyomu.scrapers.episode_page import EpisodePageScraper
from kakuyomu.scrapers.my_page import MyPageScraper
from kakuyomu.scrapers.work_page import WorkPageScraper
from kakuyomu.settings import CONFIG_DIRNAME, URL, Login
from kakuyomu.types import Diff, EpisodeId, LocalEpisode, LoginStatus, RemoteEpisode, Work, WorkId
from kakuyomu.types.episode_query import Query
from kakuyomu.types.errors import (
    CreateEpisodeFailedError,
    DeleteEpisodeFailedError,
    EpisodeAlreadyLinkedError,
    EpisodeHasNoPathError,
    EpisodeNotFoundError,
    EpisodeUpdateFailedError,
    TOMLAlreadyExistsError,
)
from kakuyomu.types.path import ConfigDir, Path

from .decorators import require_login
from .request_models import CreateEpisodeRequest
from .toc import TOCAction

logger = get_logger()


class Client:
    """Web client for kakuyomu"""

    session: requests.Session
    cwd: Path
    config_dir: ConfigDir

    def __init__(self, cwd: Path = Path.cwd(), wait_time: float = 0.1) -> None:
        """Initialize web client"""
        self.session = requests.Session()
        self.cwd = cwd
        self.wait_time = wait_time
        try:
            self.config_dir = self.cwd.config_dir
        except FileNotFoundError as e:
            logger.info(f"{e} {CONFIG_DIRNAME=} not found")
            self.config_dir = ConfigDir(Path.joinpath(cwd, CONFIG_DIRNAME))
        cookies = self._load_cookie(self.config_dir.cookie)
        if cookies:
            self.session.cookies = cookies

    def _load_cookie(self, filepath: Path) -> RequestsCookieJar | None:
        cookie: RequestsCookieJar | None
        try:
            with open(filepath, "rb") as f:
                cookie = pickle.load(f)
                return cookie
        except FileNotFoundError:
            return None
        except pickle.UnpicklingError:
            return None

    @property
    def work(self) -> Work:
        """Load work"""
        return Work.load(self.config_dir.work_toml)

    def _get(self, url: str, **kwargs) -> requests.Response:  # type: ignore
        time.sleep(self.wait_time)
        return self.session.get(url, **kwargs)

    def _post(self, url: str, **kwargs) -> requests.Response:  # type: ignore
        time.sleep(self.wait_time)
        if "headers" in kwargs:
            kwargs["headers"]["X-requested-With"] = "XMLHttpRequest"
        else:
            kwargs["headers"] = {"X-requested-With": "XMLHttpRequest"}

        return self.session.post(url, **kwargs)

    def _remove_cookie(self) -> None:
        self.config_dir.cookie.unlink(missing_ok=True)

    def status(self) -> LoginStatus:
        """Get login status"""
        res = self._get(URL.MY)
        if res.text.find("ログイン") != -1:
            return LoginStatus(is_login=False, email="")
        else:
            return LoginStatus(is_login=True, email=f"{ Login.EMAIL_ADDRESS }")

    def logout(self) -> None:
        """Logout"""
        self.session.cookies.clear()
        self._remove_cookie()

    def login(self) -> None:
        """Login"""
        res = self._get(URL.LOGIN)
        email_address = Login.EMAIL_ADDRESS
        password = Login.PASSWORD

        data = {"email_address": email_address, "password": password}

        res = self._post(URL.LOGIN, data=data)

        # save cookie to a file
        if not self.config_dir.exists():
            self.config_dir.mkdir()
        with open(self.config_dir.cookie, "wb") as f:
            pickle.dump(res.cookies, f)

    @require_login
    def get_works(self) -> dict[WorkId, Work]:
        """Get works"""
        res = self._get(URL.MY)
        html = res.text
        works = MyPageScraper(html).scrape_works()
        return works

    @require_login
    def get_remote_episodes(self) -> Sequence[RemoteEpisode]:
        """Get episodes and csrf token from work page"""
        work_id = self.work.id
        res = self._get(URL.MY_WORK.format(work_id=work_id))
        html = res.text
        scraper = WorkPageScraper(html)
        episodes = scraper.scrape_episodes()
        csrf_token = scraper.scrape_csrf_token()
        self._toc_token = csrf_token
        return episodes

    @require_login
    def fetch_remote_episodes(self) -> Diff:
        """Fetch remote episodes"""
        before_episodes = self.work.episodes

        episodes = []

        for remote_episode in self.get_remote_episodes():
            local_episode = self.get_local_episode_by_remote_episode(remote_episode)
            episodes.append(local_episode)

        work = self.work
        work.episodes = episodes

        after_episodes = work.episodes

        self._dump_work_toml(work)

        before = Query(before_episodes)
        after = Query(after_episodes)

        return before.diff(after)

    @require_login
    def link_file(self, filepath: Path) -> LocalEpisode:
        """Link file"""
        try:
            remote_episode = self._select_remote_episode()
            # set path
            local_episode = self._link_file(filepath, remote_episode)
            return local_episode
        except EpisodeAlreadyLinkedError as e:
            raise e
        except Exception as e:
            logger.error(f"予期しないエラー: {e}")
            raise e

    def _link_file(self, filepath: Path, episode: RemoteEpisode) -> LocalEpisode:
        """Link file"""
        assert episode
        work = self.work  # copy property to local variable
        result = LocalEpisode(**episode.model_dump())
        if another_episode := self.get_episode_by_path(filepath):
            logger.error(f"same path{ another_episode= }")
            raise EpisodeAlreadyLinkedError(f"同じファイルパスが既にリンクされています: {another_episode}")
        for work_episode in work.episodes:
            if work_episode.same_id(episode):
                work_episode.filepath = filepath
                logger.info(f"set filepath to episode: {episode}")
                result = work_episode
                break
        else:
            result.path = filepath
            work.episodes.append(result)
            logger.info(f"append episode: {episode}")
            result = result
        self._dump_work_toml(work)
        return result

    def unlink(self) -> LocalEpisode:
        """Unlink episode"""
        try:
            local_episode = self._select_local_episode()
            self._unlink(local_episode.id)
            return local_episode
        except EpisodeNotFoundError as e:
            raise e
        except EpisodeHasNoPathError as e:
            raise e
        except Exception as e:
            logger.error(f"予期しないエラー: {e}")
            raise e

    def _unlink(self, episode_id: EpisodeId) -> LocalEpisode:
        """Unlink episode"""
        work = self.work  # copy property to local variable
        for episode in work.episodes:
            if episode.id == episode_id:
                if not episode.path:
                    raise EpisodeHasNoPathError(f"エピソードにファイルパスが設定されていません: {episode}")
                episode.path = None
                self._dump_work_toml(work)
                return episode
        else:
            raise EpisodeNotFoundError(f"エピソードが見つかりません: {episode_id}")

    def get_episode_by_id(self, episode_id: str) -> LocalEpisode:
        """Get episode by id"""
        for episode in self.work.episodes:
            if episode.id == episode_id:
                return episode
        raise EpisodeNotFoundError(f"エピソードが見つかりません: {episode_id} {self.work.episodes}")

    def get_episode_by_path(self, filepath: Path) -> LocalEpisode | None:
        """Get episode by path"""
        logger.debug(f"local episodes: { self.work.episodes }")
        for episode in self.work.episodes:
            if episode.path == filepath:
                return episode
        return None

    def get_local_episode_by_remote_episode(self, remote_episode: RemoteEpisode) -> LocalEpisode:
        """Get episode by remote episode"""
        assert self.work
        for episode in self.work.episodes:
            if episode.same_id(remote_episode):
                return episode
        return LocalEpisode(id=remote_episode.id, title=remote_episode.title)

    @require_login
    def create_remote_episode(self, title: str, filepath: Path) -> None:
        """Create episode as draft"""
        # check if file exists
        if not filepath.exists():
            logger.error(f"file not found: {filepath}")
            raise FileNotFoundError(f"file not found: {filepath}")

        # check if episode already exists
        if self.get_episode_by_path(filepath):
            logger.error(f"episode already exists: {filepath}")
            raise EpisodeAlreadyLinkedError(f"episode already exists: {filepath}")

        before_episodes = self.get_remote_episodes()

        url = URL.NEW_EPISODE.format(work_id=self.work.id)
        with open(filepath, "r") as f:
            body = f.read()
            data = CreateEpisodeRequest(title=title, body=body).model_dump()

            res = self._post(
                url,
                data=data,
            )

            result = res.json()  # {"location":"/my/works/99999999999"} episode id返してくれない
            if res.status_code != 200:
                logger.error(f"{ result= }")
                raise CreateEpisodeFailedError(f"create episode failed: {res}")
            else:
                logger.debug(f"{ result= }")
                logger.info(f"created episode: {title=}")

        after_episodes = self.get_remote_episodes()
        new_episode = (set(after_episodes) - set(before_episodes)).pop()

        self._link_file(filepath, new_episode)

    @require_login
    def delete_remote_episodes(self, episodes: Iterable[EpisodeId]) -> None:
        """Delete episodes"""
        url = URL.EDIT_TOC.format(work_id=self.work.id)
        token = self._toc_token
        data = TOCAction.delete(csrf_token=token, episodes=episodes).model_dump()
        if len(list(episodes)) == 0:
            return
        res = self._post(url, data=data)
        if res.status_code != 200:
            logger.error(f"{res=}")
            raise DeleteEpisodeFailedError(f"delete failed: {episodes=}")

    @require_login
    def update_remote_episode(self) -> RemoteEpisode:
        """Update remote episodes"""
        remote_episode = self._select_remote_episode()
        self._update_remote_episode(remote_episode.id)
        return remote_episode

    def _update_remote_episode(self, episode_id: EpisodeId, title: str = "", body: Iterable[str] = []) -> None:
        """
        Update remote episode

        Args:
        ----
            episode_id: Episode ID
            title: title
            body: body

        Raises:
        ------
            EpisodeUpdateFailedError: error occurred while updating episode
        """
        local_episode = self.get_episode_by_id(episode_id)

        url = URL.EPISODE.format(work_id=self.work.id, episode_id=episode_id)
        params: dict[str, str] = {}

        local_title = title if title else local_episode.title
        params["title"] = local_title
        local_body = "\n".join(body if body else local_episode.body())
        params["body"] = local_body

        html = self._get(url).text
        scraper = EpisodePageScraper(html)
        csrf_token = scraper.scrape_csrf_token()
        params["csrf_token"] = csrf_token
        status = scraper.scrape_status()
        params.update(status)

        res = self._post(url, data=params)
        if res.status_code != 200:
            logger.error(f"{res.status_code=} {res.text=}")
            raise EpisodeUpdateFailedError(f"update failed: {res}")

    @require_login
    def initialize_work(self) -> None:
        """Initialize work"""
        # check if work toml already exists
        if self.config_dir.work_toml.exists():
            logger.error(f"work toml already exists. {self.work}")
            raise TOMLAlreadyExistsError(f"work.tomlはすでに存在します {self.work}")

        works = self.get_works()
        work_list = list(works.values())
        for i, work in enumerate(work_list):
            print(f"{i}: {work}")

        try:
            number = int(input("タイトルを数字で選択してください: "))
            work = work_list[number]
            self._dump_work_toml(work)
        except ValueError:
            raise ValueError("数字を入力してください")
        except IndexError:
            raise ValueError("選択された番号が存在しません")

    @require_login
    def get_remote_episode(self, episode_id: EpisodeId) -> RemoteEpisode:
        """Get remote episode"""
        episodes: Sequence[RemoteEpisode] = self.get_remote_episodes()
        for episode in episodes:
            if episode.id == episode_id:
                return episode

        raise EpisodeNotFoundError(f"エピソードが見つかりません: {episode_id}")

    def _get_remote_episode_body(self, episode_id: EpisodeId) -> Iterable[str]:
        """Get episode body"""
        res = self._get(URL.EPISODE.format(work_id=self.work.id, episode_id=episode_id))
        html = res.text
        scraper = EpisodePageScraper(html)
        # 最初の改行は削除
        body = scraper.scrape_body().lstrip("\n")
        return body.split("\n")

    @require_login
    def get_remote_episode_body(self) -> Iterable[str]:
        """Get episode body"""
        try:
            remote_episode = self._select_remote_episode()
            body: Iterable[str] = self._get_remote_episode_body(remote_episode.id)
            return body
        except ValueError:
            raise ValueError("数字を入力してください")
        except IndexError:
            raise ValueError("選択された番号が存在しません")

    def _dump_work_toml(self, work: Work) -> None:
        """Initialize work"""
        toml_path = self.config_dir.work_toml
        if toml_path.exists():
            logger.info(f"work toml {toml_path=} already exists. override {work}")

        with open(toml_path, "w") as f:
            toml.dump(work.model_dump(), f)

        logger.info(f"dump work toml: {work}")

    def _select_remote_episode(self) -> RemoteEpisode:
        """Select remote episode"""
        episodes: Sequence[RemoteEpisode] = self.get_remote_episodes()
        for i, episode in enumerate(episodes):
            print(f"{i}: {episode}")
        try:
            number = int(input("タイトルを数字で選択してください: "))
            episode = episodes[number]
            print(f"selected: {episode}")
            return episode
        except ValueError:
            raise ValueError("数字を入力してください")
        except IndexError:
            raise ValueError("選択された番号が存在しません")
        except Exception as e:
            logger.error(f"予期しないエラー: {e}")
            raise e

    def _select_local_episode(self) -> LocalEpisode:
        """Select local episode"""
        for i, episode in enumerate(self.work.episodes):
            print(f"{i}: {episode}")
        try:
            number = int(input("タイトルを数字で選択してください: "))
            episode = self.work.episodes[number]
            print(f"selected: {episode}")
            return episode
        except ValueError:
            raise ValueError("数字を入力してください")
        except IndexError:
            raise ValueError("選択された番号が存在しません")
        except Exception as e:
            logger.error(f"予期しないエラー: {e}")
            raise e
