import pickle
import os

import requests

from kakuyomu.scrapers.my_page import MyPageScraper
from kakuyomu.scrapers.work_page import WorkPageScraper
from kakuyomu.settings import URL, Config, Login, WorkConfig
from kakuyomu.types import Episode, EpisodeId, LoginStatus, Work, WorkId


class Client:
    session: requests.Session
    cookie: requests.cookies.RequestsCookieJar

    def __init__(self, cookie_path: str = Config.COOKIE):
        self.session = requests.Session()
        cookies = self._load_cookie(cookie_path)
        if cookies:
            self.session.cookies = cookies

    def _load_cookie(self, filepath: str):
        try:
            with open(filepath, "rb") as f:
                cookie = pickle.load(f)
                return cookie
        except FileNotFoundError:
            return None
        except pickle.UnpicklingError:
            return None

    def _get(self, url, **kwargs):
        return self.session.get(url, **kwargs)

    def _post(self, url, **kwargs):
        return self.session.post(url, **kwargs)

    def status(self) -> bool:
        res = self._get(URL.MY)
        if res.text.find("ログイン") != -1:
            return LoginStatus(is_login=False, email="")
        else:
            return LoginStatus(is_login=True, email="Config.EMAIL_ADDRESS")

    def logout(self) -> None:
        self.session.cookies.clear()
        if os.path.exists(Config.COOKIE):
            os.remove(Config.COOKIE)

    def login(self):
        res = self._get(URL.LOGIN)
        email_address = Login.EMAIL_ADDRESS
        password = Login.PASSWORD

        data = {"email_address": email_address, "password": password}
        headers = {"X-requested-With": "XMLHttpRequest"}

        res = self._post(URL.LOGIN, data=data, headers=headers)

        # save cookie to a file
        filepath = Config.COOKIE
        with open(filepath, "wb") as f:
            pickle.dump(res.cookies, f)

    def get_works(self) -> dict[WorkId, Work]:
        res = self._get(URL.MY)
        html = res.text
        works = MyPageScraper(html).scrape_works()
        return works

    def get_episodes(self, work_id: WorkId = WorkConfig.ID) -> dict[EpisodeId, Episode]:
        res = self._get(URL.MY_WORK.format(work_id=work_id))
        html = res.text
        episodes = WorkPageScraper(html).scrape_episodes()
        return episodes
