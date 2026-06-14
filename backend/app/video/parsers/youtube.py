from urllib.parse import parse_qs, urlparse

from app.video.parsers.generic import GenericVideoParser


class YouTubeVideoParser(GenericVideoParser):
    platform = "youtube"

    def match(self, url: str) -> bool:
        host = self.domain(url)
        return host.endswith("youtube.com") or host.endswith("youtu.be")

    def parse(self, url: str, html: str):
        metadata = super().parse(url, html)
        metadata.platform = self.platform
        video_id = self._video_id(url)
        if video_id:
            metadata.final_url = f"https://www.youtube.com/watch?v={video_id}"
        return metadata

    def _video_id(self, url: str) -> str | None:
        parsed = urlparse(url)
        if parsed.hostname and parsed.hostname.endswith("youtu.be"):
            return parsed.path.strip("/") or None
        return parse_qs(parsed.query).get("v", [None])[0]
