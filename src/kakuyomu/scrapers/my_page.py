"""Scrape my page."""

from kakuyomu.types import Work, WorkId

from .base import ScraperBase


class MyPageScraper(ScraperBase):
    """Class for scrape my page."""

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
