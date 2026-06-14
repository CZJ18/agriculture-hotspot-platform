import json
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
from app.models.crawler_request import CrawlerRequestTask
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

    def create_request(self, platform: str, *, include_hotspots: bool = True, limit: int = 50) -> dict:
        if platform != "all" and platform not in CRAWLERS:
            raise CrawlerError(f"Unsupported platform: {platform}")
        task = CrawlerRequestTask(platform=platform, include_hotspots=include_hotspots, limit=limit, status="pending")
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return self.request_to_dict(task)

    def get_request(self, request_id: int) -> dict | None:
        task = self.db.get(CrawlerRequestTask, request_id)
        return self.request_to_dict(task) if task else None

    def list_requests(self, limit: int = 50) -> list[dict]:
        stmt = select(CrawlerRequestTask).order_by(CrawlerRequestTask.created_at.desc()).limit(limit)
        return [self.request_to_dict(task) for task in self.db.execute(stmt).scalars()]

    def run_request(self, request_id: int) -> None:
        task = self.db.get(CrawlerRequestTask, request_id)
        if task is None:
            return
        task.status = "running"
        task.error_message = None
        self.db.commit()
        try:
            if task.platform == "all":
                results = self.crawl_all_stable()
                task.saved = sum(int(item.get("saved") or 0) for item in results)
                task.result = json.dumps({"results": results}, ensure_ascii=False)
            else:
                result = self.crawl_platform(task.platform)
                task.saved = int(result.get("saved") or 0)
                task.result = json.dumps(result, ensure_ascii=False)
            task.status = "completed"
        except CrawlerAuthRequired as exc:
            task.status = "auth_required"
            task.error_message = exc.message
            task.login_url = exc.login_url
            task.cookie_env = exc.cookie_env
            task.result = json.dumps(exc.to_dict(), ensure_ascii=False)
        except CrawlerError as exc:
            task.status = "error"
            task.error_message = str(exc)
            task.result = json.dumps({"status": "error", "platform": task.platform, "message": str(exc)}, ensure_ascii=False)
        finally:
            task.finished_at = datetime.utcnow()
            self.db.commit()

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

    def request_to_dict(self, task: CrawlerRequestTask) -> dict:
        result = self._loads_result(task.result)
        payload = {
            "id": task.id,
            "requestId": task.id,
            "platform": task.platform,
            "status": task.status,
            "saved": task.saved,
            "includeHotspots": task.include_hotspots,
            "limit": task.limit,
            "result": result,
            "errorMessage": task.error_message,
            "loginUrl": task.login_url,
            "cookieEnv": task.cookie_env,
            "createdAt": task.created_at,
            "updatedAt": task.updated_at,
            "finishedAt": task.finished_at,
        }
        if task.include_hotspots and task.status == "completed":
            platform = None if task.platform == "all" else task.platform
            payload["hotspots"] = self.list_hotspots(platform=platform, limit=task.limit)
        else:
            payload["hotspots"] = []
        return payload

    def _loads_result(self, value: str | None) -> dict:
        if not value:
            return {}
        try:
            decoded = json.loads(value)
        except json.JSONDecodeError:
            return {"message": value}
        return decoded if isinstance(decoded, dict) else {"value": decoded}
