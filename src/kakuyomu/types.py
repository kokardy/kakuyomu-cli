from typing import TypeAlias

from pydantic import BaseModel

WorkId: TypeAlias = str
EpisodeId: TypeAlias = str


class Work(BaseModel):
    id: WorkId
    title: str


class Episode(BaseModel):
    id: WorkId
    title: str
