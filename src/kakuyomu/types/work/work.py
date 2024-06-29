"""Define type around work"""

from typing import TypedDict

import toml
from pydantic import BaseModel
from pydantic.functional_serializers import field_serializer
from pydantic.functional_validators import field_validator

from kakuyomu.logger import logger
from kakuyomu.types.path import Path

from .episode import EpisodeId, LocalEpisode, LocalEpisodeDict

type WorkId = str  # type: ignore[valid-type]


class WorkDict(TypedDict):
    """Work dict"""

    id: WorkId
    title: str
    episodes: list[LocalEpisodeDict]


class Work(BaseModel):
    """Work model"""

    id: WorkId
    title: str
    # episodes: list["LocalEpisode"] = []
    episodes: dict["EpisodeId", "LocalEpisode"] = {}

    @field_validator("episodes", mode="before")
    @classmethod
    def _validate_episodes(cls, episodes: list[LocalEpisodeDict]) -> dict[EpisodeId, LocalEpisode]:
        """Validate episodes"""
        return {episode["id"]: LocalEpisode(**episode) for episode in episodes}

    @field_serializer("episodes")
    def serialize_episodes(self, episodes: dict[EpisodeId, LocalEpisode]) -> list[LocalEpisodeDict]:
        """Serialize episodes"""
        return [episode.dump() for episode in episodes.values()]

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
