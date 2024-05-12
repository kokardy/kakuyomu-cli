"""Scrape my page."""
import bs4

from kakuyomu.types import Work, WorkId


class MyPageScraper:
    """Class for scrape my page."""

    html: str

    def __init__(self, html: str):
        """Initialize MyPageScraper"""
        self.html = html
        self.soup = bs4.BeautifulSoup(self.html, "html.parser")

    def scrape_works(self) -> dict[WorkId, Work]:
        """Scrape works from my page"""
        links = self.soup.find_all("h2", class_="workColumn-workTitle")
        result = {}
        for link in links:
            work_id = link.a.get("href").split("/")[-1]
            work_title = link.a.text
            work = Work(id=work_id, title=work_title)
            result[work_id] = work
        return result

    def scrape_login_user(self) -> str:
        """Scrape login user from my page"""
        try:
            user = self.soup.select_one("div.names")
            assert user
            author = user.select_one("div[itemprop='author']")
            assert author
        except AssertionError as e:
            print(e)
            return ""
        return author.text
