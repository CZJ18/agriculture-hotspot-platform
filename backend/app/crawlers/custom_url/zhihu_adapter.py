from urllib.parse import urlparse

from app.crawlers.custom_url.generic_adapter import GenericAdapter


class ZhihuAdapter(GenericAdapter):
    platform = "zhihu"

    def match(self, url: str) -> bool:
        return "zhihu.com" in (urlparse(url).hostname or "").lower()
