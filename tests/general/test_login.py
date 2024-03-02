"""Test for login"""
import os
from typing import Callable

from kakuyomu.client import Client
from kakuyomu.types import LocalEpisode, RemoteEpisode, Work

from ..helper import EpisodeExistsTest

here = os.path.abspath(os.path.dirname(__file__))

work = Work(
    id="16816927859498193192",
    title="アップロードテスト用",
)
episode = LocalEpisode(
    id="16816927859880032697",
    title="第4話",
)

episodes = [
    RemoteEpisode(id="16816927859859822600", title="第1話"),
    RemoteEpisode(id="16816927859880032697", title="第4話"),
    RemoteEpisode(id="16816927859880026113", title="第2話"),
    RemoteEpisode(id="16816927859880029939", title="第3話"),
    RemoteEpisode(id="16816927860079743550", title="第4話"),
    RemoteEpisode(id="16816927860079843351", title="第5話"),
    RemoteEpisode(id="16816927860079889260", title="第6話"),
    RemoteEpisode(id="16816927860079921252", title="第7話"),
    RemoteEpisode(id="16816927860265371490", title="第8話"),
]


class TestConnectToKakuyomu(EpisodeExistsTest):
    """
    kakuyomu.jpとの疎通を伴うテスト

    疎通確認のためのテスト
    kakuyomuとの通信をmockにしない
    """

    def setup_method(self, method: Callable[..., None]) -> None:
        """Create work and episode"""
        super().setup_method(method)
        if not self.client.status().is_login:
            self.client.login()

    def teardown_method(self, method: Callable[..., None]) -> None:
        """Remove all created episodes"""
        super().teardown_method(method)
        current_episodes = self.client.get_episodes()
        delete_ids = [_episode.id for _episode in current_episodes if _episode.id not in {e.id for e in episodes}]
        self.client.delete_remote_episodes(episodes=[delete_ids])

    def test_status_not_login(self, logout_client: Client) -> None:
        """Test status not login"""
        status = logout_client.status()
        assert not status.is_login

    def test_status_login(self, login_client: Client) -> None:
        """Test status login"""
        login_client.login()
        status = login_client.status()
        assert status.is_login

    def test_work_list(self) -> None:
        """Work list test"""
        works = self.client.get_works()
        assert work.id in works
        assert works[work.id].title == work.title

    def test_episode_list(self) -> None:
        """Episode list test"""
        episodes = self.client.get_episodes()
        assert episode.id in {episodes.id for episodes in episodes}
        index = [episode.id for episode in episodes].index(episode.id)
        assert index > -1
        assert episodes[index].title == episode.title

    def test_create_and_delete_episode(self) -> None:
        """
        Create episode test

        エピソードが増えることを確認する
        エピソードが増えたら削除する
        """
        client = self.client
        # before
        before_episodes = client.get_episodes()
        client.create_remote_episode(title="テスト001", file_path=os.path.join(self.client.work_dir, "publish/001.txt"))
        # after
        after_episodes = client.get_episodes()

        diff = set(after_episodes) - set(before_episodes)
        assert len(diff) == 1
        new_episode = diff.pop()

        client.delete_remote_episodes(episodes=[new_episode.id])

        final_episodes = client.get_episodes()
        assert len(before_episodes) == len(final_episodes)

        # check linked episode
        assert new_episode.id in {episode.id for episode in client.work.episodes}

    def test_get_remote_episode_body(self) -> None:
        """
        Get remote episode body test

        取得されたエピソードの内容を検証する
        """
        body_rows = self.client._get_remote_episode_body(episode.id)
        body = "\n".join(body_rows)
        assert body.strip() == "test"
