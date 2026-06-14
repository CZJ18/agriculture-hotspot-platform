from collections.abc import Iterable

from bs4 import BeautifulSoup

from app.crawlers.base import BaseCrawler, CrawlerAuthRequired, CrawlerError, HotspotItem


class ZhihuCrawler(BaseCrawler):
    platform = "zhihu"
    login_url = "https://www.zhihu.com/signin"
    cookie_env = "ZHIHU_COOKIE"
    api_url = "https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total?limit=50&desktop=true"
    public_page_url = "https://www.zhihu.com/topsearch"

    def __init__(self) -> None:
        super().__init__()
        self.use_cookie(self.settings.zhihu_cookie, referer="https://www.zhihu.com/hot")

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

        try:
            items = self._fetch_public_page()
            if items:
                return items
        except CrawlerAuthRequired:
            raise
        except CrawlerError as exc:
            errors.append(str(exc))

        fallback = self.fallback_items("zhihu")
        if fallback:
            return fallback
        raise CrawlerError("Zhihu hot list could not be fetched from public anonymous endpoints. " + " | ".join(errors))

    def _fetch_api(self) -> list[HotspotItem]:
        data = self.parse_json(self.get(self.api_url))
        raw_items = data.get("data") or []
        if not isinstance(raw_items, list):
            raise CrawlerError("Zhihu API returned an unexpected data shape.")
        items = []
        for rank, item in enumerate(raw_items, start=1):
            target = item.get("target") if isinstance(item, dict) else {}
            if not isinstance(target, dict):
                continue
            title = target.get("title") or target.get("question", {}).get("title")
            if not title:
                continue
            url = target.get("url") or target.get("link", {}).get("url") or self.search_url(title)
            items.append(
                HotspotItem(
                    platform=self.platform,
                    rank=rank,
                    title=title,
                    url=url,
                    heat=item.get("detail_text"),
                    category="qa",
                    author=None,
                    summary=target.get("excerpt"),
                )
            )
        return items

    def _fetch_public_page(self) -> list[HotspotItem]:
        response = self.get(self.public_page_url)
        soup = BeautifulSoup(response.text, "html.parser")
        if soup.title and "安全验证" in soup.title.get_text():
            raise CrawlerAuthRequired(
                platform=self.platform,
                login_url=self.login_url,
                cookie_env=self.cookie_env,
                message="Zhihu public page returned security verification; complete login/verification in browser and set ZHIHU_COOKIE.",
            )
        items = []
        for rank, node in enumerate(soup.select('a[href*="/search"], a[href*="/question/"]'), start=1):
            title = node.get_text(" ", strip=True)
            if len(title) < 2:
                continue
            href = node.get("href") or self.search_url(title)
            if href.startswith("/"):
                href = f"https://www.zhihu.com{href}"
            items.append(HotspotItem(platform=self.platform, rank=rank, title=title, url=href, category="qa"))
            if len(items) >= 50:
                break
        return items
