"""Module for scraping episode page."""

import re

from kakuyomu.types.work.episode import PublishReservationStatus

from .base import ScraperBase


class PublishPageScraper(ScraperBase):
    """Class for scrape my page."""

    script_id = "__NEXT_DATA__"
    regex = re.compile(r""".*toBePublishedAt.*""")
    reserved_regex = re.compile(r""".*"toBePublishedAt"\s*:\s*"(?P<to_be_published_at>[^"]+)".*""")
    draft_regex = re.compile(r""".*"toBePublishedAt"\s*:\s*(null).*""")

    def scrape_status(self) -> PublishReservationStatus:
        """
        Scrape status

        <script id="__NEXT_DATA__" type="application/json">
            ...
                                "toBePublishedAt": "2024-07-04T09:00:37Z"
            ...
        """
        tag = self.soup.select_one(f"script#{self.script_id}")
        if not tag:
            raise ValueError(f"{self.script_id} not found")
        contents = tag.text
        matcher = self.regex.match(contents)
        if not matcher:
            raise ValueError(f"toBePublishedAt not found: {contents=}")

        line = matcher.group(0)

        draft_matcher = self.draft_regex.match(line)
        if draft_matcher:
            return PublishReservationStatus.from_str(None)

        reserved_matcher = self.reserved_regex.match(line)
        if not reserved_matcher:
            raise ValueError(f"unexpected format 'toBePublishedAt': {line}")

        to_be_published_at = reserved_matcher.group("to_be_published_at")
        if not isinstance(to_be_published_at, str):
            raise ValueError(f"toBePublishedAt is not str: {to_be_published_at=}")

        if to_be_published_at == "null":
            return PublishReservationStatus.from_str(None)
        to_be_published_at = to_be_published_at.strip('"')

        return PublishReservationStatus.from_str(to_be_published_at)
