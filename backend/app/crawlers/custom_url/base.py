from abc import ABC, abstractmethod
from dataclasses import dataclass
from urllib.parse import urlparse


@dataclass
class ParsedPage:
    url: str
    domain: str
    platform: str
    title: str | None = None
    description: str | None = None
    content_excerpt: str | None = None


class CustomUrlAdapter(ABC):
    platform = "generic"

    def match(self, url: str) -> bool:
        return False

    def domain(self, url: str) -> str:
        return (urlparse(url).hostname or "").lower()

    @abstractmethod
    def parse(self, url: str, html: str) -> ParsedPage:
        raise NotImplementedError
