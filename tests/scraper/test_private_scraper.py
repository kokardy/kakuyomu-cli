"""Test for Scrapers"""

import os
from typing import ClassVar, Final

from kakuyomu.scrapers.private_page import PrivatePageScraper

birth_day: Final[str] = "2025年01月09日"
email: Final[str] = "test@gmail.com"
user_id: Final[str] = "test_user_id"

template_path: Final[str] = os.path.join(os.path.dirname(__file__), "private.html")
html: Final[str] = open(template_path).read()


class TestPrivateScraper:
    """Test for PrivatePageScraper."""

    html: ClassVar[str]

    @classmethod
    def setup_class(cls) -> None:
        """Initialize class variables."""
        cls.html = (
            open(template_path)
            .read()
            .format(
                birth_day=birth_day,
                email=email,
                user_id=user_id,
            )
        )

    def test_scrape_email(self):
        """Test for scrape_email."""
        scraper = PrivatePageScraper(self.html)
        assert scraper.scrape_email() == email

    def test_scrape_id(self):
        """Test for scrape_id."""
        scraper = PrivatePageScraper(self.html)
        assert scraper.scrape_id() == user_id
