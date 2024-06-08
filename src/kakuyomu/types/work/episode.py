"""Define types around episode"""
import datetime
from collections.abc import Iterable
from typing import Annotated

from pydantic import BaseModel, ConfigDict, PlainSerializer, PlainValidator, ValidationInfo

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
