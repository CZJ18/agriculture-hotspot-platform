from collections.abc import Iterable

from app.crawlers.base import BaseCrawler, CrawlerAuthRequired, CrawlerError, HotspotItem


class YouTubeCrawler(BaseCrawler):
    platform = "youtube"
    login_url = "https://console.cloud.google.com/apis/credentials"
    cookie_env = "YOUTUBE_API_KEY"
    api_url = "https://www.googleapis.com/youtube/v3/videos"

    def fetch(self) -> Iterable[HotspotItem]:
        if not self.settings.youtube_api_key:
            raise CrawlerAuthRequired(
                platform=self.platform,
                login_url=self.login_url,
                cookie_env=self.cookie_env,
                message="YouTube Data API requires YOUTUBE_API_KEY. Create an API key in Google Cloud Console.",
            )

        data = self.parse_json(
            self.get(
                f"{self.api_url}"
                f"?part=snippet,statistics"
                f"&chart=mostPopular"
                f"&maxResults=50"
                f"&regionCode={self.settings.youtube_region_code}"
                f"&key={self.settings.youtube_api_key}"
            )
        )
        if data.get("error"):
            raise CrawlerError(f"YouTube API error: {data['error']}")

        raw_items = data.get("items") or []
        if not isinstance(raw_items, list):
            raise CrawlerError("YouTube API returned an unexpected data shape.")

        items = []
        for rank, item in enumerate(raw_items, start=1):
            if not isinstance(item, dict):
                continue
            video_id = item.get("id")
            snippet = item.get("snippet") or {}
            stats = item.get("statistics") or {}
            title = snippet.get("title")
            if not video_id or not title:
                continue
            items.append(
                HotspotItem(
                    platform=self.platform,
                    rank=rank,
                    title=title,
                    url=f"https://www.youtube.com/watch?v={video_id}",
                    heat=str(stats.get("viewCount") or ""),
                    category=str(snippet.get("categoryId") or "video"),
                    author=snippet.get("channelTitle"),
                    summary=snippet.get("description"),
                )
            )
        if not items:
            raise CrawlerError("YouTube API returned no items.")
        return items
