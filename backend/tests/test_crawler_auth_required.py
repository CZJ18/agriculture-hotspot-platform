import unittest
from unittest.mock import Mock

from app.crawlers.base import BaseCrawler, CrawlerAuthRequired


class AuthRequiredCrawler(BaseCrawler):
    platform = "auth_test"
    login_url = "https://example.com/login"

    def fetch(self):
        return []


class CrawlerAuthRequiredTests(unittest.TestCase):
    def test_get_maps_401_403_to_auth_required(self) -> None:
        crawler = AuthRequiredCrawler()
        response = Mock()
        response.status_code = 403
        response.url = "https://example.com/protected"
        crawler.session.get = Mock(return_value=response)

        with self.assertRaises(CrawlerAuthRequired) as raised:
            crawler.get("https://example.com/protected")

        self.assertEqual(raised.exception.platform, "auth_test")
        self.assertEqual(raised.exception.login_url, "https://example.com/login")


if __name__ == "__main__":
    unittest.main()
