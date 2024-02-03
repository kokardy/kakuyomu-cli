"""
Fixtures for tests.

Test episodes exists.
"""
import os
from typing import Final

import pytest

from kakuyomu.client.web import Client

CONFIG_DIR: Final[str] = "tests/testdata/no_work_toml"
COOKIE_PATH: Final[str] = os.path.join(CONFIG_DIR, "kakuyomu_cookie")


def remove_cookie() -> None:
    """Remove cookie file"""
    if os.path.exists(COOKIE_PATH):
        os.remove(COOKIE_PATH)


@pytest.fixture(scope="class")
def client() -> Client:
    """Get client"""
    remove_cookie()
    client = Client(config_dir=CONFIG_DIR, cookie_path=COOKIE_PATH)
    client.login()
    return client


@pytest.fixture(scope="function")
def login_client() -> Client:
    """Get login client"""
    remove_cookie()
    client = Client(config_dir=CONFIG_DIR, cookie_path=COOKIE_PATH)
    client.login()
    return client


@pytest.fixture(scope="function")
def logout_client() -> Client:
    """Get logout client"""
    remove_cookie()
    client = Client(config_dir=CONFIG_DIR, cookie_path=COOKIE_PATH)
    return client
