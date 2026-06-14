from collections.abc import Iterable
from urllib.parse import quote_plus

from bs4 import BeautifulSoup

from app.crawlers.base import BaseCrawler, CrawlerAuthRequired, HotspotItem


class WechatChannelsCrawler(BaseCrawler):
    platform = "wechat_channels"
    login_url = "https://channels.weixin.qq.com/"
    cookie_env = "WECHAT_CHANNELS_COOKIE"
    search_url = "https://weixin.sogou.com/weixin?type=2&query={query}"
    public_query = "微信 视频号 小视频 热门"

    def __init__(self) -> None:
        super().__init__()
        self.use_cookie(self.settings.wechat_channels_cookie, referer=self.login_url)

    def fetch(self) -> Iterable[HotspotItem]:
        public_items = self._fetch_public_search()
        if public_items:
            return public_items

        fallback = self.fallback_items("wechat_channels")
        if fallback:
            return fallback
        raise CrawlerAuthRequired(
            platform=self.platform,
            login_url=self.login_url,
            cookie_env=self.cookie_env,
            message=(
                "WeChat Channels has no stable public anonymous hot-list API. "
                "Use a logged-in browser/manual export or configure HOTSPOT_FALLBACK_BASE_URL."
            ),
        )

    def _fetch_public_search(self) -> list[HotspotItem]:
        response = self.get(self.search_url.format(query=quote_plus(self.public_query)))
        soup = BeautifulSoup(response.text, "html.parser")
        items = []
        for rank, node in enumerate(soup.select(".news-list li, li[id^='sogou_vr']"), start=1):
            title_node = node.select_one(".txt-box h3 a, h3 a")
            if not title_node:
                continue
            title = title_node.get_text(" ", strip=True)
            if len(title) < 2:
                continue
            href = title_node.get("href") or self.search_url.format(query=quote_plus(title))
            if href.startswith("/"):
                href = f"https://weixin.sogou.com{href}"
            author_node = node.select_one(".account, .s-p, .txt-box .account")
            summary_node = node.select_one(".txt-info, .txt-box p")
            items.append(
                HotspotItem(
                    platform=self.platform,
                    rank=rank,
                    title=title,
                    url=href,
                    heat=None,
                    category="wechat_public_search",
                    author=author_node.get_text(" ", strip=True) if author_node else None,
                    summary=summary_node.get_text(" ", strip=True) if summary_node else None,
                )
            )
            if len(items) >= 20:
                break
        return items
