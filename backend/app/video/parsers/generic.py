from bs4 import BeautifulSoup
from urllib.parse import urlparse

from app.video.parsers.base import VideoMetadata, VideoParser


class GenericVideoParser(VideoParser):
    platform = "generic_video"

    def match(self, url: str) -> bool:
        return True

    def parse(self, url: str, html: str) -> VideoMetadata:
        soup = BeautifulSoup(html, "html.parser")
        title = self._meta(soup, "og:title") or (soup.title.get_text(" ", strip=True) if soup.title else None)
        video_url = self._meta(soup, "og:video") or self._meta(soup, "og:video:url") or self._meta(soup, "og:video:secure_url")
        return VideoMetadata(
            source_url=url,
            final_url=url,
            platform=self.domain(url).split(".")[-2] if "." in self.domain(url) else self.platform,
            title=title,
            author=self._meta(soup, "author") or self._meta(soup, "article:author"),
            description=self._meta(soup, "og:description") or self._meta_name(soup, "description"),
            thumbnail_url=self._meta(soup, "og:image"),
            duration=self._meta(soup, "video:duration"),
            published_at=self._meta(soup, "article:published_time"),
            view_count=None,
            direct_video_url=video_url if self._looks_like_direct_video(video_url) else None,
        )

    def _meta(self, soup: BeautifulSoup, property_name: str) -> str | None:
        node = soup.find("meta", attrs={"property": property_name})
        return node.get("content", "").strip() if node and node.get("content") else None

    def _meta_name(self, soup: BeautifulSoup, name: str) -> str | None:
        node = soup.find("meta", attrs={"name": name})
        return node.get("content", "").strip() if node and node.get("content") else None

    def _looks_like_direct_video(self, url: str | None) -> bool:
        if not url:
            return False
        return urlparse(url).path.lower().endswith((".mp4", ".webm", ".mov"))
