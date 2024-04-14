"""Test for initialize"""

from io import StringIO

import pytest

from kakuyomu.types import Work
from kakuyomu.types.errors import TOMLAlreadyExistsError

from ..helper import WorkTOMLNotExistsTest

work = Work(
    id="16816927859498193192",
    title="アップロードテスト用",
)


@pytest.mark.usefixtures("fake_get_works")
class TestInitialize(WorkTOMLNotExistsTest):
    """Test for initialize"""

    def test_init_no_toml(self, monkeypatch):
        """Test kakuyomu init"""
        # mock stdin
        # select work number: 0
        monkeypatch.setattr("sys.stdin", StringIO("0\n"))
        self.client.initialize_work()

        assert self.client.config_dir.work_toml.exists()
        assert self.client.work is not None
        assert self.client.work.id == work.id

    def test_init_toml_already_exists(self, monkeypatch):
        """Test kakuyomu init already exists"""
        # mock stdin
        # select work number: 0
        monkeypatch.setattr("sys.stdin", StringIO("0\n"))
        self.client.initialize_work()

        assert self.client.config_dir.work_toml.exists()

        # raise error already exists
        with pytest.raises(TOMLAlreadyExistsError):
            self.client.initialize_work()
