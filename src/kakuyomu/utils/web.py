import pickle

import requests

from kakuyomu.settings import URL, Config, Login


class Client:
    session: requests.Session
    cookie: requests.cookies.RequestsCookieJar

    def __init__(self, cookie_path: str  = Config.COOKIE ):
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
            return False
        else:
            return True

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
