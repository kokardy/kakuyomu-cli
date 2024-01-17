from kakuyomu.client import Client
from kakuyomu.types import Episode, Work

from .helper import Test

work = Work(
    id="16816927859498193192",
    title="アップロードテスト用",
)

episode = Episode(
    id="16816927859880032697",
    title="第4話",
)


class TestWork(Test):
    def test_work_list(self, client: Client) -> None:
        works = client.get_works()
        assert work.id in works
        assert works[work.id].title == work.title

    def test_episode_list(self, client: Client) -> None:
        episodes = client.get_episodes(work.id)
        assert episode.id in episodes
        assert episodes[episode.id].title == episode.title
