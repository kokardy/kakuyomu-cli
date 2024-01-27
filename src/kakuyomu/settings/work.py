"""work settings"""

import os
from typing import Final

import toml

from kakuyomu.logger import get_logger
from kakuyomu.types import Work

from .const import CONFIG_DIRNAME, WORK_FILENAME

logger = get_logger()


def find_work_dir() -> str:
    """Find work dir

    Find work dir from current working directory.
    """
    cwd = os.getcwd()
    while True:
        path = os.path.join(cwd, CONFIG_DIRNAME)
        if os.path.exists(path):
            if os.path.isdir(path):
                logger.info(f"work dir found: {cwd}")
                return cwd
        cwd = os.path.dirname(cwd)
        if cwd == "/":
            raise FileNotFoundError(f"{CONFIG_DIRNAME} not found")


def find_config_dir() -> str:
    """Find config_dir

    Find config_dir from work dir.
    """
    root = find_work_dir()
    return os.path.join(root, CONFIG_DIRNAME)


CONFIG_DIR: Final[str] = find_config_dir()
COOKIE: Final[str] = os.path.join(CONFIG_DIR, "cookie")

_work: Work | None = None


def get_work(config_dir: str | None = None) -> Work | None:
    """Load work config

    Load work config from config_dir.
    Result is caches.
    """
    if _work:
        return _work
    config_dir = config_dir or find_config_dir()
    work_file = os.path.join(config_dir, WORK_FILENAME)
    try:
        with open(work_file, "r") as f:
            config = toml.load(f)
            return Work(**config)
    except Exception:
        return None


_work = get_work()

os.makedirs(CONFIG_DIR, exist_ok=True)
