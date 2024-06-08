"""Episode test"""
# from kakuyomu.client import Client
from io import StringIO

import pytest

from kakuyomu.client.client import Client
from kakuyomu.types import EpisodeId, LocalEpisode
from kakuyomu.types.errors import EpisodeAlreadyLinkedError, EpisodeHasNoPathError
from kakuyomu.types.path import Path

from ..helper import EpisodeExistsTest, NoEpisodeTest


class EpisodeFinder:
    """Episode finder"""

    id_with_path = "16816927859859822600"
    id_without_path = "16816927859880026113"
    client: Client

    def _get_local_episode_by_id(self, episode_id: EpisodeId) -> tuple[int, LocalEpisode]:
        episodes = self.client.get_remote_episodes()
        for index, episode in enumerate(episodes):
            if episode.id == episode_id:
                return index, LocalEpisode(id=episode.id, title=episode.title)
        raise ValueError("Episode not found")


@pytest.mark.usefixtures("fake_get_remote_episodes")
class TestNoEpisode(NoEpisodeTest, EpisodeFinder):
    """Test in the case that no episode test"""

    def test_episode_list(self) -> None:
        """Episode list test"""
        episodes = self.client.get_remote_episodes()
        index, episode = self._get_local_episode_by_id(self.id_with_path)
        assert episode.id in {episode.id for episode in episodes}
        index = [episode.id for episode in episodes].index(episode.id)
        assert episodes[index].title == episode.title

    def test_episode_link(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Episode link test"""
        monkeypatch.setattr("sys.stdin", StringIO("1\n"))
        file_path = Path("./episodes/004.txt")
        assert self.client.work

        assert file_path not in {episode.path for episode in self.client.work.episodes}
        self.client.link_file(file_path)
        assert file_path in {episode.path for episode in self.client.work.episodes}

    def test_same_path_error(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Same path error test"""
        monkeypatch.setattr("sys.stdin", StringIO("1\n1\n"))
        assert self.client.work
        file_path = Path("./episodes/004.txt")
        self.client.link_file(file_path)
        with pytest.raises(EpisodeAlreadyLinkedError):
            self.client.link_file(file_path)


@pytest.mark.usefixtures("fake_get_remote_episodes")
class TestEpisodesExist(EpisodeExistsTest, EpisodeFinder):
    """Test in the case that Episode exists test"""

    def test_episode_unlink(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Episode unlink test"""
        # select a episode which has a path
        index, episode = self._get_local_episode_by_id(self.id_with_path)
        monkeypatch.setattr("sys.stdin", StringIO(f"{index}\n"))
        assert self.client.work
        linked_episode = self.client.get_episode_by_id(episode.id)
        assert linked_episode.path is not None
        self.client.unlink()
        unlinked_episode = self.client.get_episode_by_id(episode.id)
        assert unlinked_episode.path is None

    def test_episode_unlink_no_path(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Episode unlink no path test"""
        # select a episode which has no path
        index, episode = self._get_local_episode_by_id(self.id_without_path)
        monkeypatch.setattr("sys.stdin", StringIO(f"{index}\n"))
        assert self.client.work
        linked_episode = self.client.get_episode_by_id(episode.id)
        assert linked_episode.path is None
        with pytest.raises(EpisodeHasNoPathError):
            self.client.unlink()
