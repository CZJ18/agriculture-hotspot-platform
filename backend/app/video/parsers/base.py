from dataclasses import dataclass
from urllib.parse import urlparse


@dataclass
class VideoMetadata:
    source_url: str
    final_url: str
    platform: str
    title: str | None = None
    author: str | None = None
    description: str | None = None
    thumbnail_url: str | None = None
    duration: str | None = None
    published_at: str | None = None
    view_count: str | None = None
    direct_video_url: str | None = None


class VideoParser:
    platform = "generic"

    def match(self, url: str) -> bool:
        return False

    def domain(self, url: str) -> str:
        return (urlparse(url).hostname or "").lower()

    def parse(self, url: str, html: str) -> VideoMetadata:
        raise NotImplementedError
