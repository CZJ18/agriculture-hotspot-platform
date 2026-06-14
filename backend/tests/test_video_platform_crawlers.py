import unittest
from unittest.mock import Mock, patch

from app.crawlers.base import CrawlerAuthRequired
from app.crawlers.wechat_channels import WechatChannelsCrawler
from app.crawlers.youtube import YouTubeCrawler


def fake_response(payload):
    response = Mock()
    response.json.return_value = payload
    response.text = ""
    response.content = b""
    response.raise_for_status.return_value = None
    return response


class VideoPlatformCrawlerTests(unittest.TestCase):
    @patch.dict("os.environ", {"YOUTUBE_API_KEY": "test-key", "YOUTUBE_REGION_CODE": "US"})
    @patch("app.crawlers.base.BaseCrawler.get")
    def test_youtube_most_popular_api(self, get):
        from app.config import get_settings

        get_settings.cache_clear()
        get.return_value = fake_response(
            {
                "items": [
                    {
                        "id": "abc123",
                        "snippet": {
                            "title": "YouTube hot video",
                            "channelTitle": "Creator",
                            "categoryId": "24",
                            "description": "Video description",
                        },
                        "statistics": {"viewCount": "1000"},
                    }
                ]
            }
        )

        items = list(YouTubeCrawler().fetch())

        self.assertEqual(items[0].platform, "youtube")
        self.assertEqual(items[0].url, "https://www.youtube.com/watch?v=abc123")
        self.assertEqual(items[0].heat, "1000")

    @patch.dict("os.environ", {"YOUTUBE_API_KEY": ""})
    def test_youtube_requires_api_key_for_popup(self):
        from app.config import get_settings

        get_settings.cache_clear()
        with self.assertRaises(CrawlerAuthRequired) as raised:
            list(YouTubeCrawler().fetch())

        self.assertEqual(raised.exception.cookie_env, "YOUTUBE_API_KEY")

    @patch("app.crawlers.base.BaseCrawler.get")
    def test_wechat_channels_public_search_is_tried_first(self, get):
        html = """
        <html><body><ul class="news-list">
          <li>
            <div class="txt-box">
              <h3><a href="/link?url=abc">微信视频号热门内容</a></h3>
              <p class="txt-info">公开视频号相关文章摘要</p>
              <span class="account">公众号作者</span>
            </div>
          </li>
        </ul></body></html>
        """
        response = Mock()
        response.text = html
        response.headers = {"content-type": "text/html"}
        response.raise_for_status.return_value = None
        get.return_value = response

        items = list(WechatChannelsCrawler().fetch())

        self.assertEqual(items[0].platform, "wechat_channels")
        self.assertEqual(items[0].title, "微信视频号热门内容")
        self.assertEqual(items[0].url, "https://weixin.sogou.com/link?url=abc")

    @patch("app.crawlers.base.BaseCrawler.get")
    def test_wechat_channels_requires_login_when_public_search_has_no_items(self, get):
        response = Mock()
        response.text = "<html><body>no result</body></html>"
        response.headers = {"content-type": "text/html"}
        response.raise_for_status.return_value = None
        get.return_value = response

        with self.assertRaises(CrawlerAuthRequired) as raised:
            list(WechatChannelsCrawler().fetch())

        self.assertEqual(raised.exception.platform, "wechat_channels")
        self.assertEqual(raised.exception.cookie_env, "WECHAT_CHANNELS_COOKIE")


if __name__ == "__main__":
    unittest.main()
