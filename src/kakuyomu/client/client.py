"""Web client for kakuyomu"""
import datetime
import pickle
from typing import Iterable, Sequence

import toml
from requests.cookies import RequestsCookieJar

from kakuyomu.logger import get_logger
from kakuyomu.settings import CONFIG_DIRNAME, Login
from kakuyomu.types.errors import (
    EpisodeAlreadyLinkedError,
    EpisodeHasNoPathError,
    EpisodeNotFoundError,
    TOMLAlreadyExistsError,
)
from kakuyomu.types.path import ConfigDir, Path
from kakuyomu.types.work import (
    Diff,
    EpisodeId,
    EpisodeStatus,
    LocalEpisode,
    LoginStatus,
    Query,
    RemoteEpisode,
    Work,
    WorkId,
)

from .decorators import require_login
from .request_models import CreateEpisodeRequest, DeleteEpisodesRequest, UpdateEpisodeRequest
from .web import Session

logger = get_logger()


class Client:
    """Web client for kakuyomu"""

    session: Session
    cwd: Path
    config_dir: ConfigDir

    def __init__(self, cwd: Path = Path.cwd(), wait_time: float = 0.1) -> None:
        """Initialize web client"""
        self.session = Session()
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

    def status(self) -> LoginStatus:
        """Get login status"""
        my_scraper = self.session.my_page()
        user = my_scraper.scrape_login_user()
        if user:
            return LoginStatus(is_login=True, email=f"{ Login.EMAIL_ADDRESS }", name=user)
        else:
            return LoginStatus(is_login=False, email="", name=user)

    def logout(self) -> None:
        """Logout"""
        self.session.cookies.clear()
        self.config_dir.cookie.unlink(missing_ok=True)

    def login(self) -> None:
        """Login"""
        email = Login.EMAIL_ADDRESS
        password = Login.PASSWORD

        res = self.session.login(email, password)

        # save cookie to a file
        if not self.config_dir.exists():
            self.config_dir.mkdir()
        with open(self.config_dir.cookie, "wb") as f:
            pickle.dump(res.cookies, f)

    @require_login
    def get_works(self) -> dict[WorkId, Work]:
        """Get works"""
        scraper = self.session.my_page()
        works = scraper.scrape_works()
        return works

    @require_login
    def get_remote_episodes(self) -> Sequence[RemoteEpisode]:
        """Get episodes and csrf token from work page"""
        work_id = self.work.id
        scraper = self.session.work_page(work_id)
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

        with open(filepath, "r") as f:
            body = f.read()
            data = CreateEpisodeRequest(title=title, body=body)

            self.session.create_episode(self.work.id, data)

        after_episodes = self.get_remote_episodes()
        new_episode = (set(after_episodes) - set(before_episodes)).pop()

        self._link_file(filepath, new_episode)

    @require_login
    def delete_remote_episodes(self, episode_ids: Sequence[EpisodeId]) -> None:
        """Delete episodes"""
        token = self._toc_token
        data = DeleteEpisodesRequest.create_from_episode_ids(csrf_token=token, episode_ids=episode_ids)
        if len(episode_ids) == 0:
            return
        self.session.delete_episodes(self.work.id, data)

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

        local_title = title if title else local_episode.title
        local_body = "\n".join(body if body else local_episode.body())

        scraper = self.session.episode_page(self.work.id, episode_id)
        csrf_token = scraper.scrape_csrf_token()
        status = scraper.scrape_status()
        request_body = UpdateEpisodeRequest.create_from_status(
            csrf_token=csrf_token,
            title=local_title,
            body=local_body,
            status=status,
        )

        self.session.update_episode(self.work.id, episode_id, request=request_body)

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
        scraper = self.session.episode_page(self.work.id, episode_id)
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

    def _reserve_publishing_episode(self, episode_id: EpisodeId, publish_at: datetime.datetime) -> None:
        """Publish episode"""
        scraper = self.session.episode_page(self.work.id, episode_id)
        csrf_token = scraper.scrape_csrf_token()
        title = scraper.scrape_title()
        body = scraper.scrape_body()

        status = EpisodeStatus.for_reservation(publish_at)

        request_body = UpdateEpisodeRequest(
            csrf_token=csrf_token,
            title=title,
            body=body,
            status=status.status,
            edit_reservation=status.edit_reservation,
            keep_editing=status.keep_editing,
            reservation=status.reservation,
            reservation_date=status.reservation_date,
            reservation_time=status.reservation_time,
        )

        self.session.update_episode(self.work.id, episode_id, request_body)

    def reserve_publishing_episode(self, publish_at: datetime.datetime) -> None:
        """Publish episode"""
        episode = self._select_remote_episode()
        self._reserve_publishing_episode(episode.id, publish_at)
