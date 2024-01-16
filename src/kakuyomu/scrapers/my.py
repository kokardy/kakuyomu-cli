import bs4

from kakuyomu.types import WorkId, Work


class MyScraper:
    def __init__(self, html):
        self.html = html

    def scrape_works(self) -> dict[WorkId, str]:
        soup = bs4.BeautifulSoup(self.html, "html.parser")
        links = soup.find_all("h2", class_="workColumn-workTitle")
        result = {}
        for link in links:
            work_id = link.a.get("href").split("/")[-1]
            work_title = link.a.text
            work = Work(id=work_id, title=work_title)
            result[work_id] = work
        return result
