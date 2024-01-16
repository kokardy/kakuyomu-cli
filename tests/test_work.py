from kakuyomu.utils.web import Client

from .helper import Test


class TestWork(Test):
    def test_work_list(self, login_client: Client) -> None:
        client = login_client
        works = client.get_works()
        work_id = "16816927859498193192"
        title = "アップロードテスト用"
        assert work_id in works
        assert works[work_id].title == title
