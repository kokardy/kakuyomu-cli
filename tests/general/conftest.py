"""Fixtures for generic tests."""
import pytest

from kakuyomu.client import Client
from kakuyomu.types import RemoteEpisode, Work, WorkId


@pytest.fixture
def fake_get_works(mocker):
    """Mock the get method of the requests module."""
    works: dict[WorkId, Work] = {
        "16816927859498193192": Work(
            id="16816927859498193192",
            title="アップロードテスト用",
        ),
    }
    mocker.patch.object(Client, "get_works", return_value=works)


@pytest.fixture
def fake_get_episodes(mocker):
    """Mock the get method of the requests module."""
    episodes: list[RemoteEpisode] = [
        RemoteEpisode(
            id="16816927859859822600",
            title="第1話",
        ),
        RemoteEpisode(
            id="16816927859880032697",
            title="第4話",
        ),
        RemoteEpisode(
            id="16816927859880026113",
            title="第2話",
        ),
    ]
    mocker.patch.object(Client, "get_episodes", return_value=episodes)
