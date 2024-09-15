"""Scrape private page."""

from .base import ScraperBase


class PrivatePageScraper(ScraperBase):
    """Class for scrape my page."""

    def scrape_email(self) -> str:
        """Scrape email"""
        try:
            account_text = self.soup.select("div[class^='AccountText_accountText']")
            assert account_text
            assert len(account_text) > 1
            email_div = account_text[1]
            assert email_div
            return email_div.text
        except AssertionError as e:
            print(e)
            return ""

    def scrape_id(self) -> str:
        """Scrape user id"""
        try:
            tags = self.soup.select_one("a[href^='/users/']")
            assert tags
            link = tags.get("href")
            assert isinstance(link, str)
            user_id = link.strip("/users/")
            return user_id
        except AssertionError as e:
            print(e)
            return ""
