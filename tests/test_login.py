
import os

import pytest

from kakuyomu.utils.web import Client

COOKIE_PATH = "/tmp/kakuyomu_cookie"


def remove_cookie() -> None:
    if os.path.exists(COOKIE_PATH):
        os.remove(COOKIE_PATH)

@pytest.fixture
def login_client() -> Client:
    remove_cookie()
    client = Client(COOKIE_PATH)
    client.login()
    return client

@pytest.fixture
def logout_client() -> Client:
    remove_cookie()
    client = Client(COOKIE_PATH)
    return client

class TestLogin:
    # テスト毎にテスト名を表示する
    def setup_method(self, method) -> None:
        print(f"\n========== method: {method.__name__} ============")

    def test_status_not_login(self, logout_client: Client) -> None:
        status =logout_client.status()
        assert status == False

    def test_status_login(self, login_client: Client) -> None:
        login_client.login()
        status =login_client.status()
        assert status == True

