"""Scrape work page."""

import bs4

from kakuyomu.types import Episode, EpisodeId


class WorkPageScraper:
    """Class for scrape work page."""

    html: str

    def __init__(self, html: str):
        """Initialize WorkPageScraper"""
        self.html = html

    def scrape_episodes(self) -> dict[EpisodeId, Episode]:
        """Scrape episodes from work page"""
        soup = bs4.BeautifulSoup(self.html, "html.parser")
        links = soup.select("td.episode-title a")
        result: dict[EpisodeId, Episode] = {}
        for link in links:
            href = link.get("href")
            if not href or not isinstance(href, str):
                continue
            episode_id = href.split("/")[-1]
            episode_title = link.text
            episode = Episode(id=episode_id, title=episode_title)
            result[episode_id] = episode
        return result
