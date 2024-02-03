"""work settings"""

import os
from functools import lru_cache

import toml

from kakuyomu.logger import get_logger
from kakuyomu.types import Work

from .const import CONFIG_DIRNAME, WORK_FILENAME

logger = get_logger()


@lru_cache
def find_work_dir() -> str:
    """
    Find work config dir

    Find work config dir from current working directory.
    """
    cwd = os.getcwd()
    while True:
        path = os.path.join(cwd, CONFIG_DIRNAME)
        if os.path.exists(path):
            if os.path.isdir(path):
                logger.info(f"work dir found: {cwd}")
                return cwd
        cwd = os.path.dirname(cwd)
        if os.path.abspath(cwd) == os.path.abspath(os.path.sep):
            raise FileNotFoundError(f"{CONFIG_DIRNAME} not found")


@lru_cache
def get_config_dir() -> str:
    """
    Find config_dir

    Find config_dir from current work dir.
    """
    root = find_work_dir()
    return os.path.join(root, CONFIG_DIRNAME)


@lru_cache
def get_cookie_path(config_dir: str = get_config_dir()) -> str:
    """Get cookie path"""
    return os.path.join(config_dir, "cookie")


_work: Work | None = None


def get_work(work_toml: str | None = None) -> Work | None:
    """
    Load work config

    Load work config
    Result is caches.
    """
    if _work:
        return _work
    work_file = work_toml or os.path.join(get_config_dir(), WORK_FILENAME)
    try:
        with open(work_file, "r") as f:
            config = toml.load(f)
            return Work(**config)
    except FileNotFoundError:
        logger.error(f"{work_file} not found")
        return None
    except toml.TomlDecodeError as e:
        logger.error(f"Error decoding TOML: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return None


_work = get_work()

os.makedirs(get_config_dir(), exist_ok=True)
