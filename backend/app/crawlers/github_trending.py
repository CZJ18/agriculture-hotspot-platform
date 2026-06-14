from collections.abc import Iterable

from bs4 import BeautifulSoup

from app.crawlers.base import BaseCrawler, HotspotItem


class GitHubTrendingCrawler(BaseCrawler):
    platform = "github_trending"
    url = "https://github.com/trending"

    def fetch(self) -> Iterable[HotspotItem]:
        soup = BeautifulSoup(self.get(self.url).text, "html.parser")
        for rank, repo in enumerate(soup.select("article.Box-row"), start=1):
            title_node = repo.select_one("h2 a")
            if not title_node:
                continue
            title = " ".join(title_node.get_text(" ", strip=True).split())
            href = title_node.get("href", "")
            stars_node = repo.select_one("a[href$='/stargazers']")
            desc_node = repo.select_one("p")
            yield HotspotItem(
                platform=self.platform,
                rank=rank,
                title=title,
                url=f"https://github.com{href}",
                heat=stars_node.get_text(strip=True) if stars_node else None,
                category="developer",
                summary=desc_node.get_text(" ", strip=True) if desc_node else None,
            )
