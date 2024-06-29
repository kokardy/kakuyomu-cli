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
                local_episode = LocalEpisode(
                    title=episode.title,
                    id=episode.id,
                )
                return (index, local_episode)
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


@pytest.mark.usefixtures("fake_get_remote_episodes")
class TestEpisodesExist(EpisodeExistsTest, EpisodeFinder):
    """Test in the case that Episode exists test"""

    def test_episode_link(self) -> None:
        """Episode link test"""
        file_path = self.client.config_dir.work_root.joinpath(Path("./publish/004.txt"))
        assert self.client.work

        episodes = self.client.work.episodes.values()
        episode = [episode for episode in episodes if episode.rel_path is None][0]
        work_root = self.client.config_dir.work_root

        self.client._link_file(file_path, episode.id)
        episodes = self.client.work.episodes.values()
        assert file_path.absolute() in {
            _episode.path(work_root).absolute() for _episode in episodes if _episode.rel_path
        }

    def test_same_path_error(self) -> None:
        """Same path error test"""
        rel_path = "publish/001.txt"
        file_path = self.client.config_dir.work_root.joinpath(Path(rel_path))
        assert self.client.work
        episodes = self.client.work.episodes.values()

        episode = [episode for episode in episodes if episode.rel_path == rel_path][0]

        with pytest.raises(EpisodeAlreadyLinkedError):
            self.client._link_file(file_path, episode.id)

    def test_episode_unlink(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Episode unlink test"""
        # select a episode which has a path
        index, episode = self._get_local_episode_by_id(self.id_with_path)
        monkeypatch.setattr("sys.stdin", StringIO(f"{index}\n"))
        assert self.client.work
        linked_episode = self.client.get_episode_by_id(episode.id)
        assert linked_episode.rel_path is not None
        self.client.unlink(filter_text="")
        unlinked_episode = self.client.get_episode_by_id(episode.id)
        assert unlinked_episode.rel_path is None

    def test_episode_unlink_no_path(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Episode unlink no path test"""
        # select a episode which has no path
        index, episode = self._get_local_episode_by_id(self.id_without_path)
        monkeypatch.setattr("sys.stdin", StringIO(f"{index}\n"))
        assert self.client.work
        linked_episode = self.client.get_episode_by_id(episode.id)
        assert linked_episode.rel_path is None
        with pytest.raises(EpisodeHasNoPathError):
            self.client.unlink(filter_text="")
