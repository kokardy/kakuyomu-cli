"""Base class for scraper"""

import bs4


class ScraperBase:
    """BaseClass for scrape"""

    html: str

    def __init__(self, html: str):
        """Initialize"""
        self.html = html
        self.soup = bs4.BeautifulSoup(self.html, "html.parser")
