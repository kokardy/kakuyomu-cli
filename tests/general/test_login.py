"""Test for login"""

import datetime
from typing import Callable

from kakuyomu.client import Client
from kakuyomu.types import EpisodeId, LocalEpisode, Work

from ..helper import EpisodeExistsTest, NoEpisodeTest

work = Work(
    id="16816927859498193192",
    title="アップロードテスト用",
)

episode_ids: list[EpisodeId] = [
    "16816927859859822600",
    "16816927859880032697",
    "16816927859880026113",
    "16816927859880029939",
]


class TestEpisodesExist(EpisodeExistsTest):
    """
    kakuyomu.jpとの疎通を伴うテスト

    疎通確認のためのテスト
    kakuyomuとの通信をmockにしない
    """

    original_title = "編集テスト"
    original_body = [
        "# 編集テスト",
        "",
        "編集テスト用エピソードです。",
    ]
    episode: LocalEpisode

    @classmethod
    def setup_class(cls) -> None:
        """Create client"""
        super().setup_class()
        if not cls.client.status().is_login:
            cls.client.login()

        cls.episode = LocalEpisode(
            id="16816927859880029939",
            title="編集テスト",
        )
        cls.client._update_remote_episode(cls.episode.id, title=cls.original_title, body=cls.original_body)

    @classmethod
    def teardown_class(cls) -> None:
        """Restore all episodes"""
        # 元に戻す
        cls.client._update_remote_episode(cls.episode.id, title=cls.original_title, body=cls.original_body)

    def setup_method(self, method: Callable[..., None]) -> None:
        """Create work and episode"""
        super().setup_method(method)

    def teardown_method(self, method: Callable[..., None]) -> None:
        """Remove all created episodes"""
        super().teardown_method(method)
        current_episodes = self.client.get_remote_episodes()
        delete_ids = [_episode.id for _episode in current_episodes if _episode.id not in set(episode_ids)]
        self.client.delete_remote_episodes(episode_ids=delete_ids)

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
        episodes = self.client.get_remote_episodes()
        episode = self.episode
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
        before_episodes = client.get_remote_episodes()
        title = "新規作成テスト: あとで消す"
        filepath = self.client.config_dir.work_root.joinpath("publish/005.txt")
        client.create_remote_episode(title=title, filepath=filepath)
        # after
        after_episodes = client.get_remote_episodes()

        diff = set(after_episodes) - set(before_episodes)
        assert len(diff) == 1
        new_episode = diff.pop()

        client.delete_remote_episodes(episode_ids=[new_episode.id])

        final_episodes = client.get_remote_episodes()
        assert len(before_episodes) == len(final_episodes)

        # check linked episode
        assert new_episode.id in client.work.episodes

    def test_get_remote_episode_body(self) -> None:
        """
        Get remote episode body test

        取得されたエピソードの内容を検証する
        """
        episode = self.episode
        body_rows = self.client._get_remote_episode_body(episode.id)
        body = "\n".join(body_rows)
        local_body = "\n".join(self.client._get_remote_episode_body(episode.id))
        assert body.strip() == local_body.strip()

    def test_update_remote_episode(self) -> None:
        """
        Update remote episode test

        エピソードの内容を更新する
        更新された内容を取得して検証する
        """
        episode = self.episode
        remote_episode = self.client.get_remote_episode(episode.id)
        original_body = list(self.client._get_remote_episode_body(episode.id))
        original_title = remote_episode.title
        new_body = ["new body"]
        new_title = "new title"
        self.client._update_remote_episode(episode.id, title=new_title, body=new_body)

        # 更新確認
        assert original_body != new_body
        assert original_title != new_title
        remote_episode = self.client.get_remote_episode(episode.id)
        assert new_title == remote_episode.title
        assert new_body == list(self.client._get_remote_episode_body(episode.id))

    def test_publish_episode(self) -> None:
        """
        Publish episode test

        エピソードを公開する
        公開されたエピソードの内容を取得して検証する
        """
        now = datetime.datetime.now()
        publish_at = now + datetime.timedelta(days=100)
        publish_at = publish_at.replace(second=0, microsecond=0)
        episode = self.episode

        # 未公開確認
        scraper = self.client.session.publish_page(self.client.work.id, episode.id)
        episode_status = scraper.scrape_status()
        if episode_status:
            reserved_at = episode_status.scheduled_at
            assert reserved_at != publish_at

        # 公開
        self.client._reserve_publishing_episode(episode.id, publish_at)

        # 公開確認
        scraper = self.client.session.publish_page(self.client.work.id, episode.id)
        episode_status = scraper.scrape_status()

        assert episode_status.scheduled_at
        assert episode_status.scheduled_at.hour == publish_at.hour
        assert episode_status.scheduled_at.minute == publish_at.minute

        # 戻す
        self.client._cancel_reservation(episode.id)

        # 未公開確認
        scraper = self.client.session.publish_page(self.client.work.id, episode.id)
        episode_status = scraper.scrape_status()
        assert episode_status
        assert episode_status.scheduled_at is None


class TestNoEpisode(NoEpisodeTest):
    """kakuyomuとの疎通を伴うテスト.エピソードなし"""

    def test_fetch(self) -> None:
        """Fetch test"""
        before_episodes = self.client.work.episodes
        assert not before_episodes
        diff = self.client.fetch_remote_episodes()

        assert diff.appended

        after_episodes = self.client.work.episodes
        assert after_episodes

        remote_episodes = self.client.get_remote_episodes()

        assert {episode.id for episode in remote_episodes} == {episode for episode in after_episodes}
