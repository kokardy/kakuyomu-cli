"""Episode test"""
# from kakuyomu.client import Client
from kakuyomu.types import Episode, Work

from ..helper import NoEpisodesTest

work = Work(
    id="16816927859498193192",
    title="アップロードテスト用",
)

episode = Episode(
    id="16816927859880032697",
    title="第4話",
)


class TestEpisode(NoEpisodesTest):
    """Episode test"""

    def test_episode_list(self) -> None:
        """Episode list test"""
        episodes = self.client.get_episodes()
        assert episode.id in episodes
        assert episodes[episode.id].title == episode.title
