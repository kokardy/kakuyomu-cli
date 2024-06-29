"""Test for Episode type"""

from kakuyomu.types.path import Path
from kakuyomu.types.work.episode import LocalEpisode


class TestEpisode:
    """Episode type test"""

    def test_set_path(self) -> None:
        """Test set path"""
        episode = LocalEpisode(id="1", title="title")
        root = Path("tests/testdata/episode_exists")
        file = Path("tests/testdata/episode_exists/publish/001.txt")

        episode.set_path(root, file)
        assert episode.rel_path == "publish/001.txt"

    def test_dump(self) -> None:
        """Test dump"""
        episode = LocalEpisode(id="1", title="title", rel_path="path")
        dumped = episode.dump()
        assert len(dumped) == 3
        assert dumped["id"] == "1"
        assert dumped["title"] == "title"
        assert dumped["rel_path"] == "path"
