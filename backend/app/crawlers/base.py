from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from time import sleep
from typing import Any, Iterable
from urllib.parse import quote_plus

import requests
from bs4 import BeautifulSoup

from app.config import get_settings


USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/125.0.0.0 Safari/537.36 HotspotAISystem/0.1"
)


class CrawlerError(RuntimeError):
    pass


class CrawlerAuthRequired(CrawlerError):
    def __init__(
        self,
        platform: str,
        login_url: str,
        cookie_env: str,
        message: str = "Login or browser verification is required.",
    ) -> None:
        super().__init__(message)
        self.platform = platform
        self.login_url = login_url
        self.cookie_env = cookie_env
        self.message = message

    def to_dict(self) -> dict[str, str]:
        return {
            "status": "auth_required",
            "platform": self.platform,
            "login_url": self.login_url,
            "cookie_env": self.cookie_env,
            "message": self.message,
        }


@dataclass
class HotspotItem:
    platform: str
    title: str
    url: str
    rank: int | None = None
    heat: str | None = None
    category: str | None = None
    author: str | None = None
    summary: str | None = None
    captured_at: datetime = field(default_factory=datetime.utcnow)


class BaseCrawler(ABC):
    platform: str = "base"
    login_url: str = ""
    cookie_env: str = ""

    def __init__(self) -> None:
        self.settings = get_settings()
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": USER_AGENT,
                "Accept": "application/json,text/html,application/rss+xml;q=0.9,*/*;q=0.8",
                "Referer": "https://www.google.com/",
            }
        )

    def use_cookie(self, cookie: str, *, referer: str | None = None) -> None:
        if cookie:
            self.session.headers.update({"Cookie": cookie})
        if referer:
            self.session.headers.update({"Referer": referer})

    def get(self, url: str, *, retries: int = 2) -> requests.Response:
        last_error: Exception | None = None
        for attempt in range(retries + 1):
            if attempt:
                sleep(self.settings.crawler_min_interval_seconds)
            try:
                response = self.session.get(url, timeout=self.settings.request_timeout_seconds)
                if response.status_code in {401, 403}:
                    raise CrawlerAuthRequired(
                        platform=self.platform,
                        login_url=self.login_url or url,
                        cookie_env=self.cookie_env,
                        message=f"{self.platform} returned HTTP {response.status_code}; login or verification is required.",
                    )
                response.raise_for_status()
                return response
            except CrawlerAuthRequired:
                raise
            except requests.RequestException as exc:
                last_error = exc
        raise CrawlerError(f"{self.platform} request failed: {last_error}") from last_error

    def parse_json(self, response: requests.Response) -> dict[str, Any]:
        try:
            data = response.json()
        except ValueError as exc:
            raise CrawlerError(f"{self.platform} returned non-JSON content.") from exc
        if not isinstance(data, dict):
            raise CrawlerError(f"{self.platform} returned an unexpected JSON shape.")
        return data

    def fallback_items(self, source: str | None = None) -> list[HotspotItem]:
        if not self.settings.hotspot_fallback_base_url:
            return []
        url = f"{self.settings.hotspot_fallback_base_url.rstrip('/')}/{source or self.platform}"
        response = self.get(url)
        content_type = response.headers.get("content-type", "").lower()
        if "json" in content_type:
            return self._items_from_fallback_json(self.parse_json(response))
        return self._items_from_fallback_html(response.text, url)

    def _items_from_fallback_json(self, data: dict[str, Any]) -> list[HotspotItem]:
        raw_items = data.get("data") or data.get("items") or data.get("list") or []
        if isinstance(raw_items, dict):
            raw_items = raw_items.get("list") or raw_items.get("items") or []
        if not isinstance(raw_items, list):
            return []
        items = []
        for rank, item in enumerate(raw_items, start=1):
            if not isinstance(item, dict):
                continue
            title = item.get("title") or item.get("name") or item.get("word") or item.get("note")
            if not title:
                continue
            items.append(
                HotspotItem(
                    platform=self.platform,
                    rank=rank,
                    title=str(title),
                    url=str(item.get("url") or item.get("link") or item.get("mobileUrl") or ""),
                    heat=str(item.get("hot") or item.get("heat") or item.get("num") or item.get("hot_value") or ""),
                    category=self.platform,
                    summary=str(item.get("desc") or item.get("description") or "") or None,
                )
            )
        return items

    def _items_from_fallback_html(self, html: str, base_url: str) -> list[HotspotItem]:
        soup = BeautifulSoup(html, "html.parser")
        items = []
        for rank, node in enumerate(soup.select("a"), start=1):
            title = node.get_text(" ", strip=True)
            if len(title) < 2:
                continue
            href = node.get("href") or base_url
            items.append(
                HotspotItem(
                    platform=self.platform,
                    rank=rank,
                    title=title[:200],
                    url=str(href),
                    heat=None,
                    category=self.platform,
                )
            )
            if len(items) >= 50:
                break
        return items

    def search_url(self, keyword: str) -> str:
        return f"https://www.baidu.com/s?wd={quote_plus(keyword)}"

    @abstractmethod
    def fetch(self) -> Iterable[HotspotItem]:
        raise NotImplementedError
