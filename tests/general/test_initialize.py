"""Test for initialize"""

import os
from io import StringIO
from typing import Callable

import pytest

from kakuyomu.client import Client
from kakuyomu.types import Work
from kakuyomu.types.errors import TOMLAlreadyExists

from ..helper import Case, Test, createClient

work = Work(
    id="16816927859498193192",
    title="アップロードテスト用",
)


class TestInitialize(Test):
    """Test for initialize"""

    client: Client

    # initialize class
    def setup_class(self) -> None:
        """Create client with no work.toml file."""
        self.client = createClient(case=Case.NO_WORK_TOML)

    # run before all test functions
    def setup_method(self, method: Callable[..., None]) -> None:
        """Create client"""
        super().setup_method(method)
        if os.path.exists(self.client.work_toml_path):
            os.remove(self.client.work_toml_path)

    # run after all test functions
    def teardown_method(self, method: Callable[..., None]) -> None:
        """Delete toml file"""
        super().teardown_method(method)
        if os.path.exists(self.client.work_toml_path):
            os.remove(self.client.work_toml_path)

    def test_init_no_toml(self, monkeypatch):
        """Test kakuyomu init"""
        # mock stdin
        # select work number: 0
        monkeypatch.setattr("sys.stdin", StringIO("0\n"))
        self.client.initialize_work()

        assert os.path.exists(self.client.work_toml_path)
        assert self.client.work.id == work.id

    def test_init_toml_already_exists(self, monkeypatch):
        """Test kakuyomu init already exists"""
        # mock stdin
        # select work number: 0
        monkeypatch.setattr("sys.stdin", StringIO("0\n"))
        self.client.initialize_work()

        assert os.path.exists(self.client.work_toml_path)

        # raise error already exists
        with pytest.raises(TOMLAlreadyExists):
            self.client.initialize_work()
