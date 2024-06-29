"""Fixtures for generic tests."""

import pytest
from pytest_mock import MockFixture

from kakuyomu.client import Client
from kakuyomu.types import RemoteEpisode, Work, WorkId


@pytest.fixture
def fake_get_works(mocker: MockFixture) -> None:
    """Mock the get method of the requests module."""
    works: dict[WorkId, Work] = {
        "16816927859498193192": Work(
            id="16816927859498193192",
            title="アップロードテスト用",
        ),
    }
    mocker.patch.object(Client, "get_works", return_value=works)


@pytest.fixture
def fake_get_remote_episodes(mocker: MockFixture) -> None:
    """Mock the get method of the requests module."""
    episodes: list[RemoteEpisode] = [
        RemoteEpisode(
            id="16816927859859822600",
            title="ルビテスト",
        ),
        RemoteEpisode(
            id="16816927859880032697",
            title="傍点テスト",
        ),
        RemoteEpisode(
            id="16816927859880026113",
            title="公開予約テスト",
        ),
        RemoteEpisode(
            id="16816927859880029939",
            title="編集テスト",
        ),
    ]
    mocker.patch.object(Client, "get_remote_episodes", return_value=episodes)
