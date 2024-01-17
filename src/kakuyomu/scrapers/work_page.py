import bs4

from kakuyomu.types import Episode, EpisodeId, Work


class WorkPageScraper:
    def __init__(self, html):
        self.html = html

    def scrape_episodes(self) -> dict[EpisodeId, Episode]:
        soup = bs4.BeautifulSoup(self.html, "html.parser")
        links = soup.select("td.episode-title a")
        result = {}
        for link in links:
            href = episode_id = link.get("href")
            if not href:
                continue
            episode_id = href.split("/")[-1]
            episode_title = link.text
            episode = Work(id=episode_id, title=episode_title)
            result[episode_id] = episode
        return result
