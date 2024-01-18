import os
from functools import lru_cache
from typing import Any, Final

import toml

from kakuyomu.logger import get_logger
from kakuyomu.types import WorkConfig

logger = get_logger()
config_dirname = ".kakuyomu"
work_config_file_name = "config.toml"


def find_work_dir() -> str:
    cwd = os.getcwd()
    while True:
        path = os.path.join(cwd, config_dirname)
        if os.path.exists(path):
            if os.path.isdir(path):
                logger.info(f"work dir found: {cwd}")
                return cwd
        cwd = os.path.dirname(cwd)
        if cwd == "/":
            raise FileNotFoundError(f"{config_dirname} not found")


def find_config_dir() -> str:
    root = find_work_dir()
    return os.path.join(root, config_dirname)


class ConstMeta(type):
    def __setattr__(self, name: str, value: Any) -> None:
        if name in self.__dict__:
            raise TypeError(f"cannot reassign const {name!r}")
        else:
            self.__setattr__(name, value)

    def __delattr__(self, name: str) -> None:
        if name in self.__dict__:
            raise TypeError(f"cannot delete const {name!r}")


class URL(metaclass=ConstMeta):
    ROOT: Final[str] = "https://kakuyomu.jp"
    LOGIN: Final[str] = f"{ROOT}/login"
    MY: Final[str] = f"{ROOT}/my"
    MY_WORK: Final[str] = f"{MY}/works/" + "{work_id}"
    ANNTENA_WORKS: Final[str] = f"{ROOT}/anntena/works"


class Login(metaclass=ConstMeta):
    EMAIL_ADDRESS: Final[str] = os.environ.get("KAKUYOMU_EMAIL_ADDRESS", "")
    PASSWORD: Final[str] = os.environ.get("KAKUYOMU_PASSWORD", "")


class Config(metaclass=ConstMeta):
    DIR: Final[str] = find_config_dir()
    COOKIE: Final[str] = os.path.join(DIR, "cookie")


@lru_cache(maxsize=5)
def work_config(config_dir: str = Config.DIR) -> WorkConfig:
    work_file = os.path.join(config_dir, work_config_file_name)
    with open(work_file, "r") as f:
        return WorkConfig(**toml.load(f))


class WorkSettings(metaclass=ConstMeta):
    ID: Final[str] = work_config().id


os.makedirs(Config.DIR, exist_ok=True)

if not Login.PASSWORD or not Login.EMAIL_ADDRESS:
    raise ValueError("KAKUYOMU_EMAIL_ADDRESS and KAKUYOMU_PASSWORD must be set")
