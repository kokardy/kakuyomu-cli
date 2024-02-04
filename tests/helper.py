"""テスト用のヘルパー関数を定義するモジュール"""
import enum
import logging
from typing import Callable

import coloredlogs

from kakuyomu.client import Client
from kakuyomu.logger import get_logger

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)


class Case(enum.Enum):
    """Test case"""

    NO_WORK_TOML = "no_work_toml"
    NO_EPISODES = "no_episodes"


def createClient(case: Case) -> Client:
    """Create client"""
    cwd = f"tests/testdata/{case.value}"
    client = Client(cwd=cwd)
    if not client.status().is_login:
        client.login()
    return client


class Test:
    """テスト毎にテスト名を表示する"""

    def teardown_method(self, method: Callable[..., None]) -> None:
        """テストメソッドの後にテスト名を表示する"""
        logger.debug(f"\n========== END {self.__class__} method: {method.__name__} ============")

    def setup_method(self, method: Callable[..., None]) -> None:
        """テストメソッドの前にテスト名を表示する"""
        logger.debug(f"\n========== START {self.__class__} method: {method.__name__} ============")


def set_color() -> None:
    """Set color for logger"""
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
