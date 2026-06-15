import unittest

from fastapi.testclient import TestClient

from app.database import engine, init_db
from app.main import app


class ResourceApiTests(unittest.TestCase):
    @classmethod
    def tearDownClass(cls) -> None:
        engine.dispose()

    def setUp(self) -> None:
        init_db()
        self.client = TestClient(app)

    def tearDown(self) -> None:
        self.client.close()

    def test_video_category_topic_notification_flow(self) -> None:
        category = self.client.post(
            "/api/resources/categories",
            json={
                "name": "智慧农业",
                "parent": None,
                "icon": "sprout",
                "order": 1,
                "status": "启用",
                "description": "农业科技视频分类",
            },
        )
        self.assertEqual(category.status_code, 200)
        category_id = category.json()["id"]

        video = self.client.post(
            "/api/resources/videos",
            json={
                "title": "农业无人机巡田",
                "source": "Bilibili",
                "sourceUrl": "https://www.bilibili.com/video/BV123",
                "category": "智慧农业",
                "tags": ["无人机", "植保"],
                "description": "无人机巡田演示",
                "cover": "https://example.com/cover.jpg",
                "duration": "03:20",
                "views": 100,
                "favorite": False,
                "notes": "",
            },
        )
        self.assertEqual(video.status_code, 200)
        video_id = video.json()["id"]

        filtered = self.client.get("/api/resources/videos", params={"keyword": "无人机", "category": "智慧农业", "sort": "latest"})
        self.assertEqual(filtered.status_code, 200)
        self.assertGreaterEqual(filtered.json()["total"], 1)

        favorite = self.client.post(f"/api/resources/videos/{video_id}/favorite", json={"favorite": True})
        self.assertEqual(favorite.status_code, 200)
        self.assertTrue(favorite.json()["favorite"])

        notes = self.client.patch(f"/api/resources/videos/{video_id}/notes", json={"notes": "适合首页推荐"})
        self.assertEqual(notes.status_code, 200)
        self.assertEqual(notes.json()["notes"], "适合首页推荐")

        topic = self.client.post(
            "/api/resources/topics",
            json={"title": "农业机器人专题", "description": "机器人与无人机", "accent": "green"},
        )
        self.assertEqual(topic.status_code, 200)
        topic_id = topic.json()["id"]
        add_video = self.client.post(f"/api/resources/topics/{topic_id}/videos", json={"videoId": video_id})
        self.assertEqual(add_video.status_code, 200)
        self.assertEqual(add_video.json()["video"]["id"], video_id)
        self.assertIn("playUrl", add_video.json()["video"])
        self.assertIn("downloadStatus", add_video.json()["video"])
        self.assertIn("videoInfo", add_video.json()["video"])
        topic_videos = self.client.get(f"/api/resources/topics/{topic_id}/videos")
        self.assertEqual(topic_videos.status_code, 200)
        self.assertEqual(topic_videos.json()["total"], 1)

        tree = self.client.get("/api/resources/categories/tree")
        self.assertEqual(tree.status_code, 200)
        self.assertGreaterEqual(len(tree.json()), 1)

        notification = self.client.post(
            "/api/resources/notifications",
            json={"title": "采集完成", "message": "农业无人机视频已入库"},
        )
        self.assertEqual(notification.status_code, 200)
        mark_read = self.client.patch(f"/api/resources/notifications/{notification.json()['id']}/read")
        self.assertEqual(mark_read.status_code, 200)
        self.assertTrue(mark_read.json()["read"])

        delete_category = self.client.delete(f"/api/resources/categories/{category_id}")
        self.assertEqual(delete_category.status_code, 200)


if __name__ == "__main__":
    unittest.main()
