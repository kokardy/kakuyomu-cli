"""Scrape work page."""

import bs4

from kakuyomu.types import RemoteEpisode


class WorkPageScraper:
    """Class for scrape work page."""

    html: str

    def __init__(self, html: str):
        """Initialize WorkPageScraper"""
        self.html = html
        self.soup = bs4.BeautifulSoup(html, "html.parser")

    def scrape_episodes(self) -> list[RemoteEpisode]:
        """Scrape episodes from work page"""
        links = self.soup.select("td.episode-title a")
        result: list[RemoteEpisode] = []
        for link in links:
            href = link.get("href")
            if not href or not isinstance(href, str):
                continue
            episode_id = href.split("/")[-1]
            episode_title = link.text
            episode = RemoteEpisode(id=episode_id, title=episode_title)
            result.append(episode)
        return result

    def scrape_csrf_token(self) -> str:
        """Scrape csrf token from work page"""
        tag = self.soup.select_one("input[name=csrf_token]")
        if not tag:
            raise ValueError("csrf_token not found")
        csrf_token = tag.get("value")
        if not isinstance(csrf_token, str):
            raise ValueError("csrf_token is not str")
        return csrf_token
