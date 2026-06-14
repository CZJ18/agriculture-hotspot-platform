import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.database import engine, init_db
from app.main import app


class CrawlerRequestApiTests(unittest.TestCase):
    @classmethod
    def tearDownClass(cls) -> None:
        engine.dispose()

    def setUp(self) -> None:
        init_db()
        self.client = TestClient(app)

    def tearDown(self) -> None:
        self.client.close()

    @patch("app.services.crawler_service.CrawlerService.crawl_platform")
    def test_request_returns_before_result_polling(self, crawl_platform) -> None:
        crawl_platform.return_value = {"platform": "github_trending", "saved": 2}

        response = self.client.post(
            "/api/crawler/request",
            json={"platform": "github_trending", "includeHotspots": False, "limit": 10},
        )

        self.assertEqual(response.status_code, 202)
        payload = response.json()
        self.assertEqual(payload["status"], "accepted")
        self.assertEqual(payload["platform"], "github_trending")
        self.assertIn("requestId", payload)

        status = self.client.get(f"/api/crawler/requests/{payload['requestId']}")
        self.assertEqual(status.status_code, 200)
        self.assertEqual(status.json()["status"], "completed")
        self.assertEqual(status.json()["saved"], 2)

    def test_request_rejects_unknown_platform(self) -> None:
        response = self.client.post("/api/crawler/request", json={"platform": "missing_platform"})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"]["status"], "error")


if __name__ == "__main__":
    unittest.main()
