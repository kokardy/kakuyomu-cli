import os

import pytest

from kakuyomu.logger import get_logger
from kakuyomu.client.web import Client

COOKIE_PATH = "/tmp/kakuyomu_cookie"


def set_color() -> None:
    import coloredlogs

    coloredlogs.DEFAULT_LEVEL_STYLES = {
        "critical": {"color": "red", "bold": True},
        "error": {"color": "red"},
        "warning": {"color": "yellow"},
        "notice": {"color": "magenta"},
        "info": {},
        "debug": {"color": "green"},
        "spam": {"color": "green", "faint": True},
        "success": {"color": "green", "bold": True},
        "verbose": {"color": "blue"},
    }
    logger = get_logger()
    coloredlogs.install(level="INFO", logger=logger, fmt="%(asctime)s : %(message)s", datefmt="%Y/%m/%d %H:%M:%S")
    coloredlogs.install(level="DEBUG", logger=logger, fmt="%(asctime)s : %(message)s", datefmt="%Y/%m/%d %H:%M:%S")
    coloredlogs.install(level="WARN", logger=logger, fmt="%(asctime)s : %(message)s", datefmt="%Y/%m/%d %H:%M:%S")


set_color()


def remove_cookie() -> None:
    if os.path.exists(COOKIE_PATH):
        os.remove(COOKIE_PATH)


@pytest.fixture(scope="class")
def client() -> Client:
    remove_cookie()
    client = Client(COOKIE_PATH)
    client.login()
    return client


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
