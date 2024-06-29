"""Module for scraping episode page."""

from typing import Any

import bs4

from kakuyomu.types.errors import EpisodeBodyNotFoundError
from kakuyomu.types.work import EpisodeStatus

from .base import ScraperBase


class EpisodePageScraper(ScraperBase):
    """Class for scrape my page."""

    def scrape_title(self) -> str:
        """Scrape title from episode page"""
        tag = self.soup.select_one("input[name='title']")
        if not tag:
            raise ValueError("title not found")
        title = tag.get("value")
        if not isinstance(title, str):
            raise ValueError("title is not str")
        return title

    def scrape_body(self) -> str:
        """Scrape body text from episode page"""
        textarea = self.soup.select_one("textarea[name='body']")
        if not textarea:
            raise EpisodeBodyNotFoundError(f"Textarea<name=body> not found: {textarea=}")
        if not isinstance(textarea, bs4.Tag):
            raise EpisodeBodyNotFoundError(f"Textarea<name=body> is not Tag: {textarea=}")
        body = textarea.text
        return body

    def scrape_csrf_token(self) -> str:
        """Scrape csrf_token"""
        tag = self.soup.select_one("input[name='csrf_token']")
        if not tag:
            raise ValueError("csrf_token not found")
        csrf_token = tag.get("value")
        if not isinstance(csrf_token, str):
            raise ValueError("csrf_token is not str")
        return csrf_token

    def scrape_status(self) -> EpisodeStatus:
        """Scrape status"""
        episode_status: dict[str, Any] = {}
        for key in EpisodeStatus.fields():
            tag = self.soup.select_one(f"input[name='{key}']")
            value = tag.get("value") if tag else ""
            if not isinstance(value, str):
                raise ValueError(f"{key} is not str")
            episode_status[key] = value

        return EpisodeStatus(**episode_status)
