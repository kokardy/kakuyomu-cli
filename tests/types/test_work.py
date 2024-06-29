"""Test for Work type"""
import tests.helper
from kakuyomu.types.path import Path
from kakuyomu.types.work import Work


class TestWork:
    """Test for Work type"""

    filepath = Path(tests.helper.__file__).parent.joinpath("work.toml")

    def test_load(self) -> None:
        """Test load"""
        loaded = Work.load(self.filepath)
        assert loaded

    def test_dump(self) -> None:
        """Test dump"""
        work = Work.load(self.filepath)

        dumped = work.model_dump()

        episodes = dumped["episodes"]
        assert isinstance(episodes, list)
