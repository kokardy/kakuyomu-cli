"""Episode test"""
# from kakuyomu.client import Client
from io import StringIO

import pytest

from kakuyomu.types import LocalEpisode
from kakuyomu.types.errors import EpisodeAlreadyLinkedError, EpisodeHasNoPathError

from ..helper import EpisodeExistsTest, NoEpisodesTest

episode_with_path = LocalEpisode(
    id="16816927859880032697",
    title="第4話",
)

episode_without_path = LocalEpisode(
    id="16816927859880026113",
    title="第2話",
)


@pytest.mark.usefixtures("fake_get_episodes")
class TestEpisodeNoEpisode(NoEpisodesTest):
    """Test in the case that no episode test"""

    def test_episode_list(self) -> None:
        """Episode list test"""
        episodes = self.client.get_episodes()
        episode = episode_with_path
        assert episode.id in {episode.id for episode in episodes}
        index = [episode.id for episode in episodes].index(episode.id)
        assert episodes[index].title == episode.title

    def test_episode_link(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Episode link test"""
        monkeypatch.setattr("sys.stdin", StringIO("1\n"))
        file_path = "./episodes/004.txt"
        assert self.client.work

        assert file_path not in {episode.path for episode in self.client.work.episodes}
        self.client.link_file(file_path)
        assert file_path in {episode.path for episode in self.client.work.episodes}

    def test_same_path_error(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Same path error test"""
        monkeypatch.setattr("sys.stdin", StringIO("1\n1\n"))
        assert self.client.work
        file_path = "./episodes/004.txt"
        print(self.client.work.episodes)
        self.client.link_file(file_path)
        with pytest.raises(EpisodeAlreadyLinkedError):
            self.client.link_file(file_path)


@pytest.mark.usefixtures("fake_get_episodes")
class TestEpisodeEpisodesExist(EpisodeExistsTest):
    """Test in the case that Episode exists test"""

    def test_episode_unlink(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Episode unlink test"""
        # select a episode which has a path
        monkeypatch.setattr("sys.stdin", StringIO("1\n"))
        episode = episode_with_path
        assert self.client.work
        linked_episode = self.client.get_episode_by_id(episode.id)
        assert linked_episode.path is not None
        self.client.unlink()
        unlinked_episode = self.client.get_episode_by_id(episode.id)
        assert unlinked_episode.path is None

    def test_episode_unlink_no_path(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Episode unlink no path test"""
        # select a episode which has no path
        monkeypatch.setattr("sys.stdin", StringIO("2\n"))
        episode = episode_without_path
        assert self.client.work
        linked_episode = self.client.get_episode_by_id(episode.id)
        assert linked_episode.path is None
        with pytest.raises(EpisodeHasNoPathError):
            self.client.unlink()
