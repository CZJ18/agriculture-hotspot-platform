from collections.abc import Iterable
import xml.etree.ElementTree as ET

from app.crawlers.base import BaseCrawler, HotspotItem


class NewsRSSCrawler(BaseCrawler):
    platform = "news_rss"

    feeds = [
        "https://feeds.bbci.co.uk/news/world/rss.xml",
        "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    ]

    def fetch(self) -> Iterable[HotspotItem]:
        rank = 1
        for feed_url in self.feeds:
            root = ET.fromstring(self.get(feed_url).content)
            for item in root.findall(".//item"):
                title = item.findtext("title")
                link = item.findtext("link")
                if not title or not link:
                    continue
                yield HotspotItem(
                    platform=self.platform,
                    rank=rank,
                    title=title.strip(),
                    url=link.strip(),
                    heat=None,
                    category="news",
                    author=item.findtext("author"),
                )
                rank += 1
