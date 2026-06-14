import re

from app.video.parsers.generic import GenericVideoParser


class BilibiliVideoParser(GenericVideoParser):
    platform = "bilibili"

    def match(self, url: str) -> bool:
        return "bilibili.com" in self.domain(url) or "b23.tv" in self.domain(url)

    def parse(self, url: str, html: str):
        metadata = super().parse(url, html)
        metadata.platform = self.platform
        match = re.search(r"/video/([^/?#]+)", url)
        if match:
            metadata.final_url = f"https://www.bilibili.com/video/{match.group(1)}"
        return metadata
