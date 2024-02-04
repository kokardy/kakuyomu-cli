"""Test for login"""
from kakuyomu.client import Client

from ..helper import Test


class TestLogin(Test):
    """Test for login"""

    def test_status_not_login(self, logout_client: Client) -> None:
        """Test status not login"""
        status = logout_client.status()
        assert not status.is_login

    def test_status_login(self, login_client: Client) -> None:
        """Test status login"""
        login_client.login()
        status = login_client.status()
        assert status.is_login
