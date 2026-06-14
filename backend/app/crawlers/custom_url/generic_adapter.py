from bs4 import BeautifulSoup

from app.crawlers.custom_url.base import CustomUrlAdapter, ParsedPage
from app.utils.text import compact_text


class GenericAdapter(CustomUrlAdapter):
    platform = "generic"

    def match(self, url: str) -> bool:
        return True

    def parse(self, url: str, html: str) -> ParsedPage:
        soup = BeautifulSoup(html, "html.parser")
        for node in soup(["script", "style", "noscript"]):
            node.decompose()

        title_node = soup.find("title")
        desc_node = soup.find("meta", attrs={"name": "description"}) or soup.find("meta", attrs={"property": "og:description"})
        text = compact_text(soup.get_text(" ", strip=True), limit=2000)
        return ParsedPage(
            url=url,
            domain=self.domain(url),
            platform=self.domain(url).split(".")[-2] if "." in self.domain(url) else self.domain(url),
            title=title_node.get_text(" ", strip=True) if title_node else None,
            description=desc_node.get("content", "").strip() if desc_node else None,
            content_excerpt=text,
        )
