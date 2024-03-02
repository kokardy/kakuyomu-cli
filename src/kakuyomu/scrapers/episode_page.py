"""Module for scraping episode page."""
import bs4

from kakuyomu.types.errors import EpisodeBodyNotFoundError


class EpisodePageScraper:
    """Class for scrape my page."""

    html: str

    def __init__(self, html: str):
        """Initialize"""
        self.html = html

    def scrape_body(self) -> str:
        """Scrape works from episode page"""
        soup = bs4.BeautifulSoup(self.html, "html.parser")
        textarea = soup.select_one("textarea[name='body']")
        if not textarea:
            raise EpisodeBodyNotFoundError(f"Textarea<name=body> not found: {textarea=}")
        if not isinstance(textarea, bs4.Tag):
            raise EpisodeBodyNotFoundError(f"Textarea<name=body> is not Tag: {textarea=}")
        body = textarea.text
        return body
