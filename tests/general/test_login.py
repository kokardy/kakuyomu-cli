"""Test for login"""
from kakuyomu.client import Client
from kakuyomu.types import LocalEpisode, Work

from ..helper import Test

work = Work(
    id="16816927859498193192",
    title="アップロードテスト用",
)
episode = LocalEpisode(
    id="16816927859880032697",
    title="第4話",
)


class TestLogin(Test):
    """
    Test for login

    疎通確認のためのテスト
    kakuyomuとの通信をmockにしない
    """

    def test_status_not_login(self, logout_client: Client) -> None:
        """Test status not login"""
        status = logout_client.status()
        assert not status.is_login

    def test_status_login(self, login_client: Client) -> None:
        """Test status login"""
        login_client.login()
        status = login_client.status()
        assert status.is_login

    def test_work_list(self, client: Client) -> None:
        """Work list test"""
        works = client.get_works()
        assert work.id in works
        assert works[work.id].title == work.title

    def test_episode_list(self, client: Client) -> None:
        """Episode list test"""
        episodes = client.get_episodes()
        assert episode.id in {episodes.id for episodes in episodes}
        index = [episode.id for episode in episodes].index(episode.id)
        assert index > -1
        assert episodes[index].title == episode.title
