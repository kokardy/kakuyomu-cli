"""テスト用のヘルパー関数を定義するモジュール"""

import enum
import logging

import coloredlogs

from kakuyomu.client import Client
from kakuyomu.logger import get_logger
from kakuyomu.types.path import Path

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)


class Case(enum.Enum):
    """Test case"""

    NO_WORK_TOML = "no_work_toml"
    NO_EPISODES = "no_episodes"
    EPISODES_EXISTS = "episodes_exists"


def createClient(case: Case) -> Client:
    """Create client"""
    cwd = Path(f"tests/testdata/{case.value}")
    client = Client(cwd=cwd)
    if not client.status().is_login:
        client.login()
    return client


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
