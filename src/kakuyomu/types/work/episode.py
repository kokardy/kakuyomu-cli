"""Define types around episode"""

import datetime
from collections.abc import Iterable
from typing import TypedDict

from pydantic import BaseModel, ConfigDict

from kakuyomu.settings.const import JST
from kakuyomu.types.path import Path

type EpisodeId = str  # type: ignore


class EpisodeStatus(BaseModel):
    """Episode status"""

    status: str
    edit_reservation: int
    keep_editing: int
    use_reservation: int = 1

    @staticmethod
    def fields() -> list[str]:
        """Return fields"""
        return [
            "status",
            "edit_reservation",
            "keep_editing",
            "use_reservation",
        ]


class PublishReservationStatus(BaseModel):
    """公開予約ステータス"""

    scheduled_at: datetime.datetime | None

    @classmethod
    def from_str(cls, scheduled_str: str | None) -> "PublishReservationStatus":
        """
        Set schedule from string

        "toBePublishedAt": "2024-07-04T09:00:37Z"
        """
        if scheduled_str is None:
            return cls(scheduled_at=None)
        schedule_datetime = datetime.datetime.fromisoformat(scheduled_str)
        schedule_datetime = schedule_datetime.astimezone(JST)

        return cls(scheduled_at=schedule_datetime)


class LocalEpisodeDict(TypedDict):
    """Episode dict"""

    id: EpisodeId
    title: str
    rel_path: str | None


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

    rel_path: str | None = None

    def __str__(self) -> str:
        """Return string representation of the episode"""
        return f"{self.id}:{self.title} path={self.rel_path}"

    def body(self, root: Path) -> Iterable[str]:
        """Return body text of the episode"""
        if self.rel_path is None:
            raise ValueError(f"Path is not set: {self=}")
        filepath = self.path(root)
        with open(filepath, "r") as f:
            yield from f

    def path(self, root: Path) -> Path:
        """Return path"""
        if self.rel_path is None:
            raise ValueError(f"Path is not set: {self=}")
        return Path.joinpath(root, self.rel_path)

    def set_path(self, root: Path, path: Path) -> None:
        """Set path"""
        self.rel_path = str(path.relative_to(root))

    def dump(self) -> LocalEpisodeDict:
        """Dump model"""
        return {
            "id": self.id,
            "title": self.title,
            "rel_path": self.rel_path,
        }
