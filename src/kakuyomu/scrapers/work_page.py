"""Scrape work page."""

import bs4

from kakuyomu.types import RemoteEpisode


class WorkPageScraper:
    """Class for scrape work page."""

    html: str

    def __init__(self, html: str):
        """Initialize WorkPageScraper"""
        self.html = html

    def scrape_episodes(self) -> list[RemoteEpisode]:
        """Scrape episodes from work page"""
        soup = bs4.BeautifulSoup(self.html, "html.parser")
        links = soup.select("td.episode-title a")
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
