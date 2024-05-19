"""Define types around episode"""
import datetime
from collections.abc import Iterable
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, PlainSerializer, PlainValidator, ValidationInfo, field_serializer

from kakuyomu.types.path import Path

type EpisodeId = str  # type: ignore


class EpisodeStatus(BaseModel):
    """Episode status"""

    status: str
    edit_reservation: int
    keep_editing: int
    reservation: str
    reservation_date: datetime.date | Literal[""]
    reservation_time: datetime.time | Literal[""]

    # @model_validator  # type: ignore
    # def verify_reservation(self) -> None:
    #     """Check reservation"""
    #     # 予約日が過去の場合はエラー
    #     now = datetime.datetime.now()
    #     reservation_at = datetime.datetime.combine(self.reservation_date, self.reservation_time)
    #     if now > reservation_at:
    #         raise ValueError(f"予約日が過去: {now=}, {reservation_at=}")

    @staticmethod
    def fields() -> list[str]:
        """Return fields"""
        return [
            "status",
            "edit_reservation",
            "keep_editing",
            "reservation",
            "reservation_date",
            "reservation_time",
        ]

    @field_serializer("reservation_date")
    def date_serializer(self, value: datetime.date | str) -> str:
        """
        Serialize date

        シリアライズ時にNoneを空文字に変換
        """
        if isinstance(value, str):
            return value
        return value.strftime("%Y/%m/%d")

    @field_serializer("reservation_time")
    def time_serializer(self, value: datetime.time | str) -> str:
        """
        Serialize time

        シリアライズ時にNoneを空文字に変換
        """
        if isinstance(value, str):
            return value
        return value.strftime("%H:%M")

    @classmethod
    def for_reservation(cls, publish_at: datetime.datetime) -> "EpisodeStatus":
        """
        Create status for reservation

        Example:
        -------
            status: draft
            edit_reservation: 1
            keep_editing: 0
            reservation: publishing
            reservation_date: 2024-05-23
            reservation_time: 17:00
        Args:
            publish_at: time to publish

        Returns:
        -------
            EpisodeStatus: status for reservation
        """
        return cls(
            status="draft",
            edit_reservation=1,
            keep_editing=0,
            reservation="publishing",
            reservation_date=publish_at.date(),
            reservation_time=publish_at.time(),
        )

    @classmethod
    def for_cancel_reservation(cls) -> "EpisodeStatus":
        """
        Create status for reservation cancel

        Example:
        -------
            status: draft
            edit_reservation: 1
            keep_editing: 0
            reservation_date: 2024-05-23
            reservation_time: 17:00
            reservation: cancel

        Returns:
        -------
            EpisodeStatus: status for reservation cancel
        """
        reservation_date = datetime.date.today() + datetime.timedelta(days=2)
        reservation_time = datetime.time(0, 0, 0)

        return cls(
            status="draft",
            edit_reservation=1,
            keep_editing=0,
            reservation="cancel",
            reservation_date=reservation_date,
            reservation_time=reservation_time,
        )


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
