from app.crawlers.bilibili import BilibiliCrawler
from app.crawlers.douyin import DouyinCrawler
from app.crawlers.github_trending import GitHubTrendingCrawler
from app.crawlers.hacker_news import HackerNewsCrawler
from app.crawlers.news_rss import NewsRSSCrawler
from app.crawlers.weibo import WeiboCrawler
from app.crawlers.wechat_channels import WechatChannelsCrawler
from app.crawlers.youtube import YouTubeCrawler
from app.crawlers.zhihu import ZhihuCrawler

__all__ = [
    "BilibiliCrawler",
    "DouyinCrawler",
    "GitHubTrendingCrawler",
    "HackerNewsCrawler",
    "NewsRSSCrawler",
    "WeiboCrawler",
    "WechatChannelsCrawler",
    "YouTubeCrawler",
    "ZhihuCrawler",
]
