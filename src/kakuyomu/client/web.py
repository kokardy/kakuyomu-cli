"""
Web client for kakuyomu

This module is a web client for kakuyomu.jp.
"""
import os
import pickle

import requests
import toml

from kakuyomu.logger import get_logger
from kakuyomu.scrapers.my_page import MyPageScraper
from kakuyomu.scrapers.work_page import WorkPageScraper
from kakuyomu.settings import CONFIG_DIRNAME, COOKIE_FILENAME, URL, WORK_FILENAME, Login
from kakuyomu.types import EpisodeId, LocalEpisode, LoginStatus, RemoteEpisode, Work, WorkId
from kakuyomu.types.errors import (
    EpisodeAlreadyLinkedError,
    EpisodeHasNoPathError,
    EpisodeNotFoundError,
    TOMLAlreadyExistsError,
)

from .decorators import require_login, require_work

logger = get_logger()


class Client:
    """Web client for kakuyomu"""

    session: requests.Session
    config_dir: str
    work_toml_path: str
    cookie_path: str
    work_dir: str

    def __init__(self, cwd: str = os.getcwd()) -> None:
        """Initialize web client"""
        self.session = requests.Session()
        try:
            self.config_dir = self._get_config_dir(cwd)
        except FileNotFoundError as e:
            logger.info(f"{e} {CONFIG_DIRNAME=} not found")
            self.config_dir = os.path.join(cwd, CONFIG_DIRNAME)
        self.work_toml_path = os.path.join(self.config_dir, WORK_FILENAME)
        self.cookie_path = os.path.join(self.config_dir, COOKIE_FILENAME)
        self.work_dir = os.path.dirname(self.config_dir)
        cookies = self._load_cookie(self.cookie_path)
        if cookies:
            self.session.cookies = cookies

    def _load_cookie(self, filepath: str) -> requests.cookies.RequestsCookieJar | None:
        cookie: requests.cookies.RequestsCookieJar
        try:
            with open(filepath, "rb") as f:
                cookie = pickle.load(f)
                return cookie
        except FileNotFoundError:
            return None
        except pickle.UnpicklingError:
            return None

    @property
    def work(self) -> Work | None:
        """Load work"""
        work = self._load_work_toml()
        if not work:
            logger.info("work is not set")
        return work

    def _get(self, url: str, **kwargs) -> requests.Response:  # type: ignore
        return self.session.get(url, **kwargs)

    def _post(self, url: str, **kwargs) -> requests.Response:  # type: ignore
        return self.session.post(url, **kwargs)

    def _remove_cookie(self) -> None:
        if os.path.exists(self.cookie_path):
            os.remove(self.cookie_path)

    def _set_config_dir(self, config_dir: str) -> None:
        self.config_dir = config_dir

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
        headers = {"X-requested-With": "XMLHttpRequest"}

        res = self._post(URL.LOGIN, data=data, headers=headers)

        # save cookie to a file
        if not os.path.exists(self.config_dir):
            os.mkdir(self.config_dir)
        with open(self.cookie_path, "wb") as f:
            pickle.dump(res.cookies, f)

    @require_login
    def get_works(self) -> dict[WorkId, Work]:
        """Get works"""
        res = self._get(URL.MY)
        html = res.text
        works = MyPageScraper(html).scrape_works()
        return works

    @require_work
    def get_episodes(self) -> list[RemoteEpisode]:
        """Get episodes"""
        assert self.work  # require_work decorator assures work is not None
        work_id = self.work.id
        res = self._get(URL.MY_WORK.format(work_id=work_id))
        html = res.text
        episodes = WorkPageScraper(html).scrape_episodes()
        return episodes

    @require_work
    def link_file(self, filepath: str) -> LocalEpisode:
        """Link file"""
        assert self.work  # require_work decorator assures work is not None
        episodes = self.get_episodes()
        local_episode: LocalEpisode
        for i, remote_episode in enumerate(episodes):
            print(f"{i}: {remote_episode}")
        try:
            number = int(input("タイトルを数字で選択してください: "))
            remote_episode = episodes[number]
            # path not set
            local_episode = self.get_episode_by_remote_episode(remote_episode)
            # set path
            local_episode = self._link_file(filepath, local_episode)
            return local_episode
        except EpisodeAlreadyLinkedError as e:
            raise e
        except ValueError as e:
            raise ValueError(f"数字を入力してください: {e}")
        except IndexError as e:
            raise ValueError(f"選択された番号が存在しません: {e}")
        except Exception as e:
            logger.error(f"予期しないエラー: {e}")
            raise e

    @require_work
    def _link_file(self, filepath: str, episode: RemoteEpisode) -> LocalEpisode:
        """Link file"""
        assert self.work  # require_work decorator assures work is not None
        assert episode
        work = self.work  # copy property to local variable
        result: LocalEpisode | None = None
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
            episode.path = filepath
            local_episode = LocalEpisode(**episode.model_dump())
            work.episodes.append(local_episode)
            logger.info(f"append episode: {episode}")
            result = local_episode
        self._dump_work_toml(work)
        return result

    @require_work
    def unlink(self) -> LocalEpisode:
        """Unlink episode"""
        assert self.work  # require_work decorator assures work is not None
        work = self.work  # copy property to local variable

        for i, episode in enumerate(work.episodes):
            print(f"{i}: {episode}")
        try:
            number = int(input("タイトルを数字で選択してください: "))
            episode = work.episodes[number]
            self._unlink(episode.id)
            return episode
        except EpisodeNotFoundError as e:
            raise e
        except EpisodeHasNoPathError as e:
            raise e
        except ValueError as e:
            raise ValueError(f"数字を入力してください: {e}")
        except IndexError as e :
            raise ValueError(f"選択された番号が存在しません: {e}")
        except Exception as e:
            logger.error(f"予期しないエラー: {e}")
            raise e

    @require_work
    def _unlink(self, episode_id: EpisodeId) -> LocalEpisode:
        """Unlink episode"""
        assert self.work  # require_work decorator assures work is not None
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

    @require_work
    def get_episode_by_id(self, episode_id: str) -> LocalEpisode:
        """Get episode by id"""
        assert self.work  # require_work decorator assures work is not None
        for episode in self.work.episodes:
            if episode.id == episode_id:
                return episode
        raise EpisodeNotFoundError(f"エピソードが見つかりません: {episode_id} {self.work.episodes}")

    @require_work
    def get_episode_by_path(self, filepath: str) -> LocalEpisode | None:
        """Get episode by path"""
        assert self.work  # require_work decorator assures work is not None
        logger.debug(f"local episodes: { self.work.episodes }")
        for episode in self.work.episodes:
            if episode.path == filepath:
                return episode
        return None

    @require_work
    def get_episode_by_remote_episode(self, remote_episode: RemoteEpisode) -> LocalEpisode:
        """Get episode by remote episode"""
        assert self.work
        for episode in self.work.episodes:
            if episode.same_id(remote_episode):
                return episode
        return LocalEpisode(id=remote_episode.id, title=remote_episode.title)

    @require_login
    def initialize_work(self) -> None:
        """Initialize work"""
        # check if work toml already exists
        if os.path.exists(self.work_toml_path):
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

    def _dump_work_toml(self, work: Work) -> None:
        """Initialize work"""
        filepath = self.work_toml_path
        if os.path.exists(filepath):
            logger.info(f"work toml {filepath=} already exists. override {work}")

        with open(filepath, "w") as f:
            toml.dump(work.model_dump(), f)

        logger.info(f"dump work toml: {work}")

    def _load_work_toml(self) -> Work | None:
        """
        Load work config

        Load work config
        Result is caches.
        """
        try:
            with open(self.work_toml_path, "r") as f:
                config = toml.load(f)
                return Work(**config)
        except FileNotFoundError:
            logger.info(f"{self.work_toml_path} not found")
            return None
        except toml.TomlDecodeError as e:
            logger.error(f"Error decoding TOML: {e}")
            return None
        except Exception as e:
            logger.error(f"unexpected error: {e}")
            raise e

    def _get_config_dir(self, cwd: str) -> str:
        """
        Find work config dir

        Find work config dir from current working directory.
        """
        while True:
            path = os.path.join(cwd, CONFIG_DIRNAME)
            if os.path.exists(path):
                if os.path.isdir(path):
                    logger.info(f"work dir found: {cwd}")
                    config_dir = os.path.join(cwd, CONFIG_DIRNAME)
                    return config_dir
            cwd = os.path.dirname(cwd)
            if os.path.abspath(cwd) == os.path.abspath(os.path.sep):
                raise FileNotFoundError(f"{CONFIG_DIRNAME} not found")
