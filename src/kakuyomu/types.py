"""Define type aliases and models."""

from typing import TypeAlias

from pydantic import BaseModel

WorkId: TypeAlias = str
EpisodeId: TypeAlias = str


class Work(BaseModel):
    """Work model"""

    id: WorkId
    title: str


class Episode(BaseModel):
    """Episode model"""

    id: WorkId
    title: str


class LoginStatus(BaseModel):
    """Login status model"""

    is_login: bool
    email: str


class WorkConfig(BaseModel):
    """Work config model"""

    id: WorkId
