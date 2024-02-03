"""
Web client for kakuyomu

This module is a web client for kakuyomu.jp.
"""
import os
import pickle

import requests

from kakuyomu.scrapers.my_page import MyPageScraper
from kakuyomu.scrapers.work_page import WorkPageScraper
from kakuyomu.settings import URL, Login, get_config_dir, get_cookie_path, get_work
from kakuyomu.types import Episode, EpisodeId, LoginStatus, Work, WorkId


class Client:
    """Web client for kakuyomu"""

    session: requests.Session
    cookie_path: requests.cookies.RequestsCookieJar
    config_dir: str

    def __init__(self, *, config_dir: str = get_config_dir(), cookie_path: str = ""):
        """Initialize web client"""
        self.session = requests.Session()
        self.config_dir = config_dir
        self.cookie_path = cookie_path or get_cookie_path(config_dir)
        cookies = self._load_cookie(cookie_path)
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
    def work(self) -> Work:
        """Load work"""
        work = get_work()
        if work is None:
            raise ValueError("work is not set")
        return work

    def _get(self, url: str, **kwargs) -> requests.Response:  # type: ignore
        return self.session.get(url, **kwargs)

    def _post(self, url: str, **kwargs) -> requests.Response:  # type: ignore
        return self.session.post(url, **kwargs)

    def status(self) -> LoginStatus:
        """Get login status"""
        res = self._get(URL.MY)
        if res.text.find("ログイン") != -1:
            return LoginStatus(is_login=False, email="")
        else:
            return LoginStatus(is_login=True, email="Config.EMAIL_ADDRESS")

    def logout(self) -> None:
        """Logout"""
        cookie = self.cookie_path
        self.session.cookies.clear()
        if os.path.exists(cookie):
            os.remove(cookie)

    def login(self) -> None:
        """Login"""
        res = self._get(URL.LOGIN)
        email_address = Login.EMAIL_ADDRESS
        password = Login.PASSWORD

        data = {"email_address": email_address, "password": password}
        headers = {"X-requested-With": "XMLHttpRequest"}

        res = self._post(URL.LOGIN, data=data, headers=headers)

        # save cookie to a file
        with open(self.cookie_path, "wb") as f:
            pickle.dump(res.cookies, f)

    def get_works(self) -> dict[WorkId, Work]:
        """Get works"""
        res = self._get(URL.MY)
        html = res.text
        works = MyPageScraper(html).scrape_works()
        return works

    def get_episodes(self, work_id: WorkId = "") -> dict[EpisodeId, Episode]:
        """Get episodes"""
        if not work_id:
            work_id = self.work.id
        res = self._get(URL.MY_WORK.format(work_id=work_id))
        html = res.text
        episodes = WorkPageScraper(html).scrape_episodes()
        return episodes
