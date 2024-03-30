"""Define type aliases and models."""

from collections.abc import Iterable
from typing import Optional

from pydantic import BaseModel, ConfigDict

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


class LocalEpisode(Episode):
    """Local episode model"""

    path: Optional[str] = None

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


class LoginStatus(BaseModel):
    """Login status model"""

    is_login: bool
    email: str
