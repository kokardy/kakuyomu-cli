"""Define type aliases and models."""

from typing import Optional, TypeAlias

from pydantic import BaseModel

WorkId: TypeAlias = str
EpisodeId: TypeAlias = str


class Episode(BaseModel):
    """Episode model"""

    id: EpisodeId
    title: str
    path: Optional[str] = None


class Work(BaseModel):
    """Work model"""

    id: WorkId
    title: str
    episodes: list[Episode] = []


class LoginStatus(BaseModel):
    """Login status model"""

    is_login: bool
    email: str
