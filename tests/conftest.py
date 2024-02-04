"""Global configuration for pytest"""


import pytest

from kakuyomu.client.web import Client

from .helper import Case, createClient, set_color

set_color()


@pytest.fixture(scope="class")
def client() -> Client:
    """Get client"""
    client = createClient(Case.NO_WORK_TOML)
    client.login()
    return client


@pytest.fixture(scope="function")
def login_client() -> Client:
    """Get login client"""
    client = createClient(Case.NO_WORK_TOML)
    client.login()
    return client


@pytest.fixture(scope="function")
def logout_client() -> Client:
    """Get logout client"""
    client = createClient(Case.NO_WORK_TOML)
    client.logout()
    return client
