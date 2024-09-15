"""CLI Settings"""

import zoneinfo
from typing import Any, Final

from kakuyomu.logger import get_logger

JST: Final[zoneinfo.ZoneInfo] = zoneinfo.ZoneInfo("Asia/Tokyo")

logger = get_logger()
CONFIG_DIRNAME: Final[str] = ".kakuyomu"
WORK_FILENAME: Final[str] = "work.toml"
COOKIE_FILENAME: Final[str] = "cookie"


class ConstMeta(type):
    """Const meta class"""

    def __setattr__(self, name: str, value: Any) -> None:
        """Deny reassign const"""
        if name in self.__dict__:
            raise TypeError(f"cannot reassign const {name!r}")
        else:
            self.__setattr__(name, value)

    def __delattr__(self, name: str) -> None:
        """Deny delete const"""
        if name in self.__dict__:
            raise TypeError(f"cannot delete const {name!r}")


class URL(metaclass=ConstMeta):
    """URL constants"""

    ROOT: Final[str] = "https://kakuyomu.jp"
    LOGIN: Final[str] = f"{ROOT}/login"
    MY: Final[str] = f"{ROOT}/my"
    MY_WORK: Final[str] = f"{MY}/works/{{work_id}}"
    NEW_EPISODE: Final[str] = f"{MY_WORK}/episodes/new"
    EDIT_TOC: Final[str] = f"{MY_WORK}/edit_toc_bulk"
    EPISODE: Final[str] = f"{MY_WORK}/episodes/{{episode_id}}"
    PUBLISH: Final[str] = f"{EPISODE}/publish"
    OPERATION: Final[str] = f"{ROOT}/graphql?opname={{opname}}"
    PRIVATE: Final[str] = f"{ROOT}/settings/private"
