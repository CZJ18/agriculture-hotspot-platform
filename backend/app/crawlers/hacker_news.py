from collections.abc import Iterable

from bs4 import BeautifulSoup

from app.crawlers.base import BaseCrawler, HotspotItem


class HackerNewsCrawler(BaseCrawler):
    platform = "hacker_news"
    url = "https://news.ycombinator.com/"

    def fetch(self) -> Iterable[HotspotItem]:
        soup = BeautifulSoup(self.get(self.url).text, "html.parser")
        rows = soup.select("tr.athing")
        for rank, row in enumerate(rows, start=1):
            title_node = row.select_one(".titleline a")
            if not title_node:
                continue
            subtext = row.find_next_sibling("tr")
            score_node = subtext.select_one(".score") if subtext else None
            author_node = subtext.select_one(".hnuser") if subtext else None
            yield HotspotItem(
                platform=self.platform,
                rank=rank,
                title=title_node.get_text(" ", strip=True),
                url=title_node.get("href", ""),
                heat=score_node.get_text(strip=True) if score_node else None,
                category="technology",
                author=author_node.get_text(strip=True) if author_node else None,
            )
