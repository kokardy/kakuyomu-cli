"""Define type aliases and models."""

from collections.abc import Iterable
from typing import Annotated

import toml
from pydantic import BaseModel, ConfigDict, PlainSerializer, PlainValidator, ValidationInfo

from kakuyomu.logger import logger
from kakuyomu.types.path import Path

type WorkId = str  # type: ignore
type EpisodeId = str  # type: ignore


class Episode(BaseModel):
    """Base episode model"""

    id: EpisodeId
    title: str

    def same_id(self, other: "Episode") -> bool:
        """Check if the id is the same"""
        return self.id == other.id

    def __str__(self) -> str:
        """Return string representation of the episode"""
        return f"{self.id}:{self.title}"


class RemoteEpisode(Episode):
    """Remote episode model"""

    model_config = ConfigDict(frozen=True)


def _validate_path(v: str | Path, info: ValidationInfo) -> Path:
    """Validate path"""
    if isinstance(v, str):
        return Path(v)
    elif isinstance(v, Path):
        return v
    else:
        raise ValueError(f"Invalid path: {v=}, {info=}")


def _serialize_path(v: Path | None) -> str | None:
    """Serialize path"""
    if v is None:
        return v
    return str(v)


PathValidator = PlainValidator(_validate_path)
PathSerializer = PlainSerializer(_serialize_path)
type AnnotatedPath = Annotated[Path, PathValidator, PathSerializer]  # type: ignore[valid-type]


class LocalEpisode(Episode):
    """Local episode model"""

    path: AnnotatedPath | None = None

    def __str__(self) -> str:
        """Return string representation of the episode"""
        return f"{self.id}:{self.title} path={self.path}"

    def body(self) -> Iterable[str]:
        """Return body text of the episode"""
        if self.path is None:
            raise ValueError(f"Path is not set: {self=}")
        with open(self.path, "r") as f:
            yield from f


class Work(BaseModel):
    """Work model"""

    id: WorkId
    title: str
    episodes: list[LocalEpisode] = []

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


class Diff(BaseModel):
    """Episodes diff model"""

    appended: list[Episode] = []
    removed: list[Episode] = []
    updated: list[Episode] = []
