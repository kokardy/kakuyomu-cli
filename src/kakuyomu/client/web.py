"""
Web client for kakuyomu

This module is a web client for kakuyomu.jp.
"""
import os
import pickle
import traceback

import requests
import toml

from kakuyomu.logger import get_logger
from kakuyomu.scrapers.my_page import MyPageScraper
from kakuyomu.scrapers.work_page import WorkPageScraper
from kakuyomu.settings import CONFIG_DIRNAME, COOKIE_FILENAME, URL, WORK_FILENAME, Login
from kakuyomu.types import Episode, EpisodeId, LoginStatus, Work, WorkId
from kakuyomu.types.errors import TOMLAlreadyExists

from .decorators import require_login, require_work

logger = get_logger()


class Client:
    """Web client for kakuyomu"""

    session: requests.Session
    cookie_path: str
    config_dir: str
    work_toml_path: str

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
    def get_episodes(self) -> dict[EpisodeId, Episode]:
        """Get episodes"""
        assert self.work  # require_work decorator assures work is not None
        work_id = self.work.id
        res = self._get(URL.MY_WORK.format(work_id=work_id))
        html = res.text
        episodes = WorkPageScraper(html).scrape_episodes()
        return episodes

    @require_login
    def initialize_work(self) -> None:
        """Initialize work"""
        # check if work toml already exists
        if os.path.exists(self.work_toml_path):
            logger.error(f"work toml already exists. {self.work}")
            raise TOMLAlreadyExists(f"work.tomlはすでに存在します {self.work}")

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
            traceback.print_stack()
            return None

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
