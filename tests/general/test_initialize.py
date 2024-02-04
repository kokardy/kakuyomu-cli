"""Test for initialize"""

import pytest
import os
from io import StringIO

from kakuyomu.types import Work
from kakuyomu.types.errors import TOMLAlreadyExists

from ..helper import Case, Test, createClient


work = Work(
    id="16816927859498193192",
    title="アップロードテスト用",
)


class TestInitialize(Test):
    """Test for initialize"""

    def test_init_no_toml(self, monkeypatch):
        """Test kakuyomu init"""
        # mock stdin
        # select work number: 0
        monkeypatch.setattr("sys.stdin", StringIO("0\n"))
        case = Case.NO_WORK_TOML

        client = createClient(case=case)
        if os.path.exists(client.work_toml_path):
            os.remove(client.work_toml_path)

        client.initialize_work()

        assert client.work_toml_path
        assert os.path.exists(client.work_toml_path)

        # new client
        client = createClient(case=case)
        assert client.work.id == work.id

        # after
        os.remove(client.work_toml_path)
        assert not os.path.exists(client.work_toml_path)

    def test_init_toml_already_exists(self, monkeypatch):
        """Test kakuyomu init already exists"""
        case = Case.NO_WORK_TOML
        # mock stdin
        # select work number: 0
        monkeypatch.setattr("sys.stdin", StringIO("0\n"))
        client = createClient(case=case)
        client.initialize_work()

        assert client.work_toml_path
        assert os.path.exists(client.work_toml_path)

        # raise error already exists
        client = createClient(case=case)
        with pytest.raises(TOMLAlreadyExists):
            client.initialize_work()
