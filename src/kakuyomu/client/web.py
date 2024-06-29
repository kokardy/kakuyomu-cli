"""
Web client for kakuyomu

This module is a web client for kakuyomu.jp.
"""

import http
import time
from typing import override

import requests

from kakuyomu.logger import get_logger
from kakuyomu.scrapers.episode_page import EpisodePageScraper
from kakuyomu.scrapers.my_page import MyPageScraper
from kakuyomu.scrapers.publish_page import PublishPageScraper
from kakuyomu.scrapers.work_page import WorkPageScraper
from kakuyomu.settings import URL
from kakuyomu.types.errors import (
    EpisodeCreateFailedError,
    EpisodeDeleteFailedError,
    EpisodeReservePublishError,
    EpisodeUpdateFailedError,
)
from kakuyomu.types.work import EpisodeId, WorkId

from .request_models import CreateEpisodeRequest, DeleteEpisodesRequest, PublishRequest, UpdateEpisodeRequest

logger = get_logger()


class Session(requests.Session):
    """Session for kakuyomu"""

    wait_time: float = 0.1

    @override
    def post(self, url, data=None, json=None, **kwargs) -> requests.Response:  # type: ignore[no-untyped-def]
        if "headers" in kwargs:
            kwargs["headers"]["X-requested-With"] = "XMLHttpRequest"
        else:
            kwargs["headers"] = {"X-requested-With": "XMLHttpRequest"}

        return super().post(url, data=data, json=json, **kwargs)

    def set_wait_time(self, wait_time: float) -> None:
        """Set wait time"""
        self.wait_time = wait_time

    def my_page(self) -> MyPageScraper:
        """Get my page"""
        time.sleep(self.wait_time)
        res = self.get(URL.MY)
        return MyPageScraper(res.text)

    def get_work_url(self, work_id: WorkId) -> str:
        """Get work url"""
        return URL.MY_WORK.format(work_id=work_id)

    def episode_url(self, work_id: WorkId, episode_id: EpisodeId) -> str:
        """Get episode url"""
        return URL.EPISODE.format(work_id=work_id, episode_id=episode_id)

    def publish_url(self, work_id: WorkId, episode_id: EpisodeId) -> str:
        """Get publish url"""
        return URL.PUBLISH.format(work_id=work_id, episode_id=episode_id)

    def work_page(self, work_id: WorkId) -> WorkPageScraper:
        """Get work page"""
        time.sleep(self.wait_time)
        url = self.get_work_url(work_id)
        res = self.get(url)
        return WorkPageScraper(res.text)

    def episode_page(self, work_id: WorkId, episode_id: EpisodeId) -> EpisodePageScraper:
        """Get episode page"""
        time.sleep(self.wait_time)
        url = self.episode_url(work_id, episode_id)
        res = self.get(url)
        return EpisodePageScraper(res.text)

    def publish_page(self, work_id: WorkId, episode_id: EpisodeId) -> PublishPageScraper:
        """Get publish page"""
        time.sleep(self.wait_time)
        url = self.publish_url(work_id, episode_id)
        res = self.get(url)
        return PublishPageScraper(res.text)

    def create_episode(self, work_id: WorkId, request: CreateEpisodeRequest) -> None:
        """Create Episode"""
        time.sleep(self.wait_time)
        url = URL.NEW_EPISODE.format(work_id=work_id)
        res = self.post(url, data=request.model_dump())
        if res.status_code != http.HTTPStatus.OK:
            # result = res.json()  # {"location":"/my/works/99999999999"} episode id返してくれない
            logger.error(f"{res.status_code=} {res.text=}")
            raise EpisodeCreateFailedError(f"create failed: {res}")
        logger.info(f"CREATE: {res.status_code=} {res.text=}")

    def update_episode(self, work_id: WorkId, episode_id: EpisodeId, request: UpdateEpisodeRequest) -> None:
        """Update Episode"""
        time.sleep(self.wait_time)
        url = self.episode_url(work_id, episode_id)
        res = self.post(url, data=request.model_dump())
        if res.status_code != http.HTTPStatus.OK:
            logger.error(f"{res.status_code=} {res.text=}")
            raise EpisodeUpdateFailedError(f"update failed: {res}")
        logger.info(f"UPDATE {episode_id}: {res.status_code=} {res.text=}")

    def delete_episodes(self, work_id: WorkId, request: DeleteEpisodesRequest) -> None:
        """Delete episodes"""
        time.sleep(self.wait_time)
        url = URL.EDIT_TOC.format(work_id=work_id)
        res = self.post(url, data=request.model_dump())
        if res.status_code != http.HTTPStatus.OK:
            logger.error(f"{res.status_code=} {res.text=}")
            raise EpisodeDeleteFailedError(f"delete failed: {res}")
        logger.info(f"DELETE {request.target_toc_item_id}: {res.status_code=} {res.text=}")

    def publish_reserve(self, work_id: WorkId, episode_id: EpisodeId, request: PublishRequest) -> None:
        """Reserve publish"""
        time.sleep(self.wait_time)
        _ = work_id
        url = URL.OPERATION.format(opname=request.operationName)
        headers = dict(
            Referer=f"https://kakuyomu.jp/my/works/{work_id}/episodes/{episode_id}/publish",
        )
        res = self.post(url, headers=headers, json=request.model_dump())
        if res.status_code != http.HTTPStatus.OK:
            logger.error(f"{res.status_code=} {res.text=}")
            raise EpisodeReservePublishError(f"delete failed: {res}")
        logger.info(f"PUBLISH {episode_id}: {res.status_code=} {res.text=}")

    def login(self, email: str, password: str) -> requests.Response:
        """Login"""
        time.sleep(self.wait_time)
        data = {"email_address": email, "password": password}
        res = self.post(URL.LOGIN, data=data)
        if res.status_code != http.HTTPStatus.OK:
            raise Exception(f"login failed: {res}")
        return res
