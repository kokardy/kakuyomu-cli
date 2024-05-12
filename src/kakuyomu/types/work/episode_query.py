"""Episode query"""

from collections.abc import Sequence
from pydantic import BaseModel

from .episode import Episode, EpisodeId


class Diff(BaseModel):
    """Episodes diff model"""

    appended: list[Episode] = []
    removed: list[Episode] = []
    updated: list[Episode] = []


class Query:
    """Episode query"""

    _dict: dict[EpisodeId, Episode]
    _list: list[Episode]

    def __init__(self, episodes: Sequence[Episode]) -> None:
        """Initialize episode query"""
        episodes = list(episodes)
        if self._exists_same_id(episodes):
            raise ValueError("Duplicated id")
        self._list = episodes
        self._dict = {episode.id: episode for episode in episodes}

    def _exists_same_id(self, episodes: Sequence[Episode]) -> bool:
        """Validate episodes"""
        ids = [episode.id for episode in episodes]
        return not len(ids) == len(set(ids))

    def get(self, episode_id: EpisodeId) -> Episode:
        """Get episode by id"""
        return self._dict[episode_id]

    def diff(self, newer: "Query") -> Diff:
        """Diff episodes"""
        appended = set(newer._dict.keys()) - set(self._dict.keys())
        removed = set(self._dict.keys()) - set(newer._dict.keys())

        updated = set()
        remains = set(self._dict.keys()) & set(newer._dict.keys())

        for remain in remains:
            if self._dict[remain] != newer._dict[remain]:
                updated.add(remain)
        return Diff(
            appended=[newer._dict[episode_id] for episode_id in appended],
            removed=[self._dict[episode_id] for episode_id in removed],
            updated=[newer._dict[episode_id] for episode_id in updated],
        )

    def __str__(self) -> str:
        """Return string representation of the query"""
        return "\n".join([episode.id for episode in self._list])
