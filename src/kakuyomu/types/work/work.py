"""Define type around work"""

import toml
from pydantic import BaseModel

from kakuyomu.logger import logger
from kakuyomu.types.path import Path

from .episode import LocalEpisode

type WorkId = str  # type: ignore


class Work(BaseModel):
    """Work model"""

    id: WorkId
    title: str
    episodes: list["LocalEpisode"] = []

    @classmethod
    def load(cls, toml_path: Path) -> "Work":
        """Load work from file"""
        if not toml_path.exists():
            raise FileNotFoundError(f"Workファイルが見つかりません: {toml_path}")
        with open(toml_path, "r") as f:
            try:
                params = toml.load(f)
                return cls(**params)
            except toml.TomlDecodeError as e:
                logger.error(f"Error decoding TOML: {e}")
                raise e
            except Exception as e:
                logger.error(f"unexpected error: {e}")
                raise e


class LoginStatus(BaseModel):
    """Login status model"""

    is_login: bool
    email: str
    name: str
