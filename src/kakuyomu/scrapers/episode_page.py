"""Module for scraping episode page."""
from dataclasses import dataclass

import bs4

from kakuyomu.types.errors import EpisodeBodyNotFoundError

"""
* Example
  * status="draft"
  * edit_reservation="0"
  * keep_editing="1"
  * reservation=""
  * reservation_date="2024-03-17"
  * reservation_time="16:00"
"""
keys = [
    "status",
    "edit_reservation",
    "keep_editing",
    "reservation",
    "reservation_date",
    "reservation_time",
]


@dataclass
class EpisodeStatus:
    """
    Episode status

    * Example
      * status="draft"
      * edit_reservation="0"
      * keep_editing="1"
      * reservation=""
      * reservation_date="2024-03-17"
      * reservation_time="16:00"
    """

    status: str
    edit_reservation: str
    keep_editing: str
    reservation: str
    reservation_date: str
    reservation_time: str


class EpisodePageScraper:
    """Class for scrape my page."""

    html: str

    def __init__(self, html: str):
        """Initialize"""
        self.html = html
        self.soup = bs4.BeautifulSoup(self.html, "html.parser")

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

    def scrape_status(self) -> dict[str, str]:
        """Scrape status"""
        episode_status: dict[str, str] = {}
        for key in keys:
            tag = self.soup.select_one(f"input[name='{key}']")
            if not tag:
                raise ValueError(f"{key} not found")
            value = tag.get("value")
            if not isinstance(value, str):
                raise ValueError(f"{key} is not str")
            episode_status[key] = value
        return episode_status
