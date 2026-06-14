import unittest
from unittest.mock import Mock, patch

from app.crawlers.bilibili import BilibiliCrawler
from app.crawlers.douyin import DouyinCrawler
from app.crawlers.weibo import WeiboCrawler
from app.crawlers.zhihu import ZhihuCrawler


def fake_response(payload):
    response = Mock()
    response.json.return_value = payload
    response.text = ""
    response.content = b""
    response.raise_for_status.return_value = None
    return response


class PlatformCrawlerTests(unittest.TestCase):
    @patch.dict("os.environ", {"ZHIHU_COOKIE": "z_c0=test-cookie"})
    def test_zhihu_cookie_is_attached_from_env(self):
        from app.config import get_settings

        get_settings.cache_clear()
        crawler = ZhihuCrawler()

        self.assertEqual(crawler.session.headers["Cookie"], "z_c0=test-cookie")

    @patch.dict("os.environ", {"WEIBO_COOKIE": "SUB=test-cookie"})
    def test_weibo_cookie_is_attached_from_env(self):
        from app.config import get_settings

        get_settings.cache_clear()
        crawler = WeiboCrawler()

        self.assertEqual(crawler.session.headers["Cookie"], "SUB=test-cookie")

    @patch("app.crawlers.base.BaseCrawler.get")
    def test_bilibili_ranking_api(self, get):
        get.return_value = fake_response(
            {
                "code": 0,
                "data": {
                    "list": [
                        {
                            "title": "B站热点",
                            "short_link_v2": "https://b23.tv/abc",
                            "tname": "知识",
                            "owner": {"name": "UP主"},
                            "stat": {"view": 1234},
                        }
                    ]
                },
            }
        )

        items = list(BilibiliCrawler().fetch())

        self.assertEqual(items[0].platform, "bilibili")
        self.assertEqual(items[0].title, "B站热点")
        self.assertEqual(items[0].heat, "1234")

    @patch("app.crawlers.base.BaseCrawler.get")
    def test_zhihu_hot_api_shape(self, get):
        get.return_value = fake_response(
            {
                "data": [
                    {
                        "target": {
                            "title": "知乎热榜",
                            "url": "https://www.zhihu.com/question/1",
                            "excerpt": "摘要",
                        },
                        "detail_text": "100 万热度",
                    }
                ]
            }
        )

        items = list(ZhihuCrawler().fetch())

        self.assertEqual(items[0].platform, "zhihu")
        self.assertEqual(items[0].title, "知乎热榜")
        self.assertEqual(items[0].heat, "100 万热度")

    @patch("app.crawlers.base.BaseCrawler.get")
    def test_weibo_hot_search_api(self, get):
        get.return_value = fake_response({"data": {"realtime": [{"note": "微博热搜", "word_scheme": "#微博热搜#", "num": 88}]}})

        items = list(WeiboCrawler().fetch())

        self.assertEqual(items[0].platform, "weibo")
        self.assertEqual(items[0].title, "微博热搜")
        self.assertEqual(items[0].heat, "88")

    @patch("app.crawlers.base.BaseCrawler.get")
    def test_douyin_hot_search_api(self, get):
        get.return_value = fake_response({"data": {"word_list": [{"word": "抖音热点", "hot_value": 99}]}})

        items = list(DouyinCrawler().fetch())

        self.assertEqual(items[0].platform, "douyin")
        self.assertEqual(items[0].title, "抖音热点")
        self.assertEqual(items[0].heat, "99")


if __name__ == "__main__":
    unittest.main()
