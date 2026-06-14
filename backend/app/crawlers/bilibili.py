from collections.abc import Iterable

from app.crawlers.base import BaseCrawler, CrawlerError, HotspotItem


class BilibiliCrawler(BaseCrawler):
    platform = "bilibili"
    login_url = "https://passport.bilibili.com/login"
    cookie_env = "BILIBILI_COOKIE"
    ranking_url = "https://api.bilibili.com/x/web-interface/ranking/v2?rid=0&type=all"

    def __init__(self) -> None:
        super().__init__()
        self.use_cookie(self.settings.bilibili_cookie, referer="https://www.bilibili.com/v/popular/rank/all")

    def fetch(self) -> Iterable[HotspotItem]:
        data = self.parse_json(self.get(self.ranking_url))
        if data.get("code") != 0:
            if data.get("code") in {-101, -352}:
                from app.crawlers.base import CrawlerAuthRequired

                raise CrawlerAuthRequired(
                    platform=self.platform,
                    login_url=self.login_url,
                    cookie_env=self.cookie_env,
                    message=f"Bilibili returned code={data.get('code')}; login, cookie refresh, or browser verification is required.",
                )
            raise CrawlerError(f"Bilibili ranking API returned code={data.get('code')}: {data.get('message')}")

        raw_items = (data.get("data") or {}).get("list") or []
        items = []
        for rank, item in enumerate(raw_items, start=1):
            title = item.get("title")
            if not title:
                continue
            bvid = item.get("bvid")
            owner = item.get("owner") or {}
            stat = item.get("stat") or {}
            items.append(
                HotspotItem(
                    platform=self.platform,
                    rank=rank,
                    title=title,
                    url=item.get("short_link_v2") or (f"https://www.bilibili.com/video/{bvid}" if bvid else "https://www.bilibili.com/v/popular/rank/all"),
                    heat=str(stat.get("view") or stat.get("like") or ""),
                    category=item.get("tname") or "video",
                    author=owner.get("name"),
                    summary=item.get("desc"),
                )
            )
        if not items:
            raise CrawlerError("Bilibili ranking API returned no items.")
        return items
