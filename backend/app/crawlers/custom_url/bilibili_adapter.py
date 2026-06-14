from urllib.parse import urlparse

from app.crawlers.custom_url.generic_adapter import GenericAdapter


class BilibiliAdapter(GenericAdapter):
    platform = "bilibili"

    def match(self, url: str) -> bool:
        return "bilibili.com" in (urlparse(url).hostname or "").lower()
