"""Test for work"""

import pytest

from kakuyomu.client import Client
from kakuyomu.types import Work

from ..helper import Test

work = Work(
    id="16816927859498193192",
    title="アップロードテスト用",
)


@pytest.mark.usefixtures("fake_get_works")
class TestWork(Test):
    """Test works and episodes"""

    def test_work_list(self, client: Client) -> None:
        """Work list test"""
        works = client.get_works()
        assert work.id in works
        assert works[work.id].title == work.title
