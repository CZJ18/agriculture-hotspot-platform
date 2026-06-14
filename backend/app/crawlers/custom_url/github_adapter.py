from urllib.parse import urlparse

from app.crawlers.custom_url.generic_adapter import GenericAdapter


class GitHubAdapter(GenericAdapter):
    platform = "github"

    def match(self, url: str) -> bool:
        return (urlparse(url).hostname or "").lower().endswith("github.com")
