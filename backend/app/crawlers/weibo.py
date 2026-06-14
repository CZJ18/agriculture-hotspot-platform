from collections.abc import Iterable
from urllib.parse import quote_plus

from bs4 import BeautifulSoup

from app.crawlers.base import BaseCrawler, CrawlerAuthRequired, CrawlerError, HotspotItem


class WeiboCrawler(BaseCrawler):
    platform = "weibo"
    login_url = "https://weibo.com/login.php"
    cookie_env = "WEIBO_COOKIE"
    api_url = "https://weibo.com/ajax/side/hotSearch"
    public_page_url = "https://s.weibo.com/top/summary?cate=realtimehot"

    def __init__(self) -> None:
        super().__init__()
        self.use_cookie(self.settings.weibo_cookie, referer="https://weibo.com/hot/search")

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

        fallback = self.fallback_items("weibo")
        if fallback:
            return fallback
        raise CrawlerError("Weibo hot search could not be fetched from public anonymous endpoints. " + " | ".join(errors))

    def _fetch_api(self) -> list[HotspotItem]:
        data = self.parse_json(self.get(self.api_url))
        raw_items = (data.get("data") or {}).get("realtime") or []
        if not isinstance(raw_items, list):
            raise CrawlerError("Weibo API returned an unexpected data shape.")
        items = []
        for rank, item in enumerate(raw_items, start=1):
            title = item.get("note") or item.get("word")
            if not title:
                continue
            scheme = item.get("word_scheme") or title
            items.append(
                HotspotItem(
                    platform=self.platform,
                    rank=rank,
                    title=title,
                    url=f"https://s.weibo.com/weibo?q={quote_plus(scheme)}",
                    heat=str(item.get("num") or item.get("raw_hot") or ""),
                    category="social",
                    summary=item.get("desc"),
                )
            )
        return items

    def _fetch_public_page(self) -> list[HotspotItem]:
        response = self.get(self.public_page_url)
        soup = BeautifulSoup(response.text, "html.parser")
        if soup.title and "Visitor" in soup.title.get_text():
            raise CrawlerAuthRequired(
                platform=self.platform,
                login_url=self.login_url,
                cookie_env=self.cookie_env,
                message="Weibo returned visitor verification; complete login/verification in browser and set WEIBO_COOKIE.",
            )
        items = []
        for rank, node in enumerate(soup.select('td.td-02 a, a[href*="/weibo?q="]'), start=1):
            title = node.get_text(" ", strip=True)
            if len(title) < 2:
                continue
            href = node.get("href") or f"https://s.weibo.com/weibo?q={quote_plus(title)}"
            if href.startswith("//"):
                href = f"https:{href}"
            elif href.startswith("/"):
                href = f"https://s.weibo.com{href}"
            items.append(HotspotItem(platform=self.platform, rank=rank, title=title, url=href, category="social"))
            if len(items) >= 50:
                break
        return items
