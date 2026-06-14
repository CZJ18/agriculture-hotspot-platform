from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.crawlers import (
    BilibiliCrawler,
    DouyinCrawler,
    GitHubTrendingCrawler,
    HackerNewsCrawler,
    NewsRSSCrawler,
    WeiboCrawler,
    WechatChannelsCrawler,
    YouTubeCrawler,
    ZhihuCrawler,
)
from app.crawlers.base import CrawlerAuthRequired, CrawlerError, HotspotItem
from app.models.hotspot import Hotspot
from app.services.serialization import dumps_list, loads_list


CRAWLERS = {
    "github_trending": GitHubTrendingCrawler,
    "hacker_news": HackerNewsCrawler,
    "news_rss": NewsRSSCrawler,
    "bilibili": BilibiliCrawler,
    "douyin": DouyinCrawler,
    "zhihu": ZhihuCrawler,
    "weibo": WeiboCrawler,
    "wechat_channels": WechatChannelsCrawler,
    "youtube": YouTubeCrawler,
}


class CrawlerService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_hotspots(self, platform: str | None = None, limit: int = 100) -> list[dict]:
        stmt = select(Hotspot).order_by(Hotspot.captured_at.desc()).limit(limit)
        if platform:
            stmt = select(Hotspot).where(Hotspot.platform == platform).order_by(Hotspot.captured_at.desc()).limit(limit)
        return [self._to_dict(item) for item in self.db.execute(stmt).scalars()]

    def crawl_platform(self, platform: str) -> dict:
        crawler_cls = CRAWLERS.get(platform)
        if not crawler_cls:
            raise CrawlerError(f"Unsupported platform: {platform}")
        items = list(crawler_cls().fetch())
        saved = self.save_items(items)
        return {"platform": platform, "saved": saved}

    def crawl_all_stable(self) -> list[dict]:
        results = []
        for platform in [
            "github_trending",
            "hacker_news",
            "news_rss",
            "bilibili",
            "zhihu",
            "weibo",
            "douyin",
            "wechat_channels",
            "youtube",
        ]:
            try:
                results.append(self.crawl_platform(platform))
            except CrawlerAuthRequired as exc:
                results.append({**exc.to_dict(), "saved": 0})
            except CrawlerError as exc:
                results.append({"platform": platform, "error": str(exc), "saved": 0})
        return results

    def save_items(self, items: list[HotspotItem]) -> int:
        for item in items:
            self.db.add(
                Hotspot(
                    platform=item.platform,
                    rank=item.rank,
                    title=item.title,
                    url=item.url,
                    heat=item.heat,
                    category=item.category,
                    author=item.author,
                    summary=item.summary,
                    keywords=dumps_list([]),
                    captured_at=item.captured_at or datetime.utcnow(),
                )
            )
        self.db.commit()
        return len(items)

    def _to_dict(self, item: Hotspot) -> dict:
        return {
            "id": item.id,
            "platform": item.platform,
            "rank": item.rank,
            "title": item.title,
            "url": item.url,
            "heat": item.heat,
            "category": item.category,
            "author": item.author,
            "summary": item.summary,
            "sentiment": item.sentiment,
            "keywords": loads_list(item.keywords),
            "captured_at": item.captured_at,
            "created_at": item.created_at,
            "updated_at": item.updated_at,
        }
