from collections.abc import Iterable
from urllib.parse import quote_plus

from app.crawlers.base import BaseCrawler, CrawlerAuthRequired, CrawlerError, HotspotItem


class DouyinCrawler(BaseCrawler):
    platform = "douyin"
    login_url = "https://www.douyin.com/"
    cookie_env = "DOUYIN_COOKIE"
    api_url = "https://www.douyin.com/aweme/v1/web/hot/search/list/?device_platform=webapp&aid=6383&channel=channel_pc_web"

    def __init__(self) -> None:
        super().__init__()
        self.use_cookie(self.settings.douyin_cookie, referer="https://www.douyin.com/hot")

    def fetch(self) -> Iterable[HotspotItem]:
        errors: list[str] = []
        try:
            items = self._fetch_api()
            if items:
                return items
        except CrawlerAuthRequired:
            raise
        except CrawlerError as exc:
            errors.append(str(exc))

        fallback = self.fallback_items("douyin")
        if fallback:
            return fallback
        raise CrawlerError("Douyin hot list could not be fetched from public anonymous endpoints. " + " | ".join(errors))

    def _fetch_api(self) -> list[HotspotItem]:
        data = self.parse_json(self.get(self.api_url))
        raw_items = (data.get("data") or {}).get("word_list") or data.get("word_list") or []
        if not isinstance(raw_items, list):
            raise CrawlerError("Douyin API returned an unexpected data shape.")
        items = []
        for rank, item in enumerate(raw_items, start=1):
            if not isinstance(item, dict):
                continue
            title = item.get("word") or item.get("sentence")
            if not title:
                continue
            items.append(
                HotspotItem(
                    platform=self.platform,
                    rank=rank,
                    title=title,
                    url=f"https://www.douyin.com/search/{quote_plus(title)}",
                    heat=str(item.get("hot_value") or item.get("event_time") or ""),
                    category="short_video",
                    summary=item.get("label"),
                )
            )
        if not items and data in ({}, {"data": None}):
            raise CrawlerError("Douyin public API returned empty data.")
        return items
