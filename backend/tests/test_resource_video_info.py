import unittest

from fastapi.testclient import TestClient

from app.database import SessionLocal, engine, init_db
from app.main import app
from app.models.video_task import VideoTask


class ResourceVideoInfoTests(unittest.TestCase):
    @classmethod
    def tearDownClass(cls) -> None:
        engine.dispose()

    def setUp(self) -> None:
        init_db()
        self.client = TestClient(app)

    def tearDown(self) -> None:
        self.client.close()

    def test_resource_video_returns_linked_download_info(self) -> None:
        with SessionLocal() as db:
            task = VideoTask(
                url="https://www.bilibili.com/video/BVagri123/",
                final_url="https://www.bilibili.com/video/BVagri123/",
                platform="bilibili",
                title="Smart agriculture harvest",
                description="Agricultural technology video",
                thumbnail_url="https://example.com/thumb.jpg",
                duration="00:28",
                view_count="1234",
                download_requested=True,
                download_status="completed",
                download_path="downloads/videos/agri.mp4",
                status="completed",
            )
            db.add(task)
            db.commit()
            db.refresh(task)
            task_id = task.id

        created = self.client.post(
            "/api/resources/videos",
            json={
                "videoTaskId": task_id,
                "category": "智慧农业",
                "tags": ["农业", "视频"],
            },
        )

        self.assertEqual(created.status_code, 200)
        payload = created.json()
        self.assertEqual(payload["videoTaskId"], task_id)
        self.assertEqual(payload["source"], "Bilibili")
        self.assertEqual(payload["sourceUrl"], "https://www.bilibili.com/video/BVagri123/")
        self.assertEqual(payload["cover"], "https://example.com/thumb.jpg")
        self.assertEqual(payload["downloadStatus"], "completed")
        self.assertEqual(payload["downloadUrl"], "/api/video/files/agri.mp4")
        self.assertEqual(payload["playUrl"], "/api/video/files/agri.mp4")
        self.assertEqual(payload["videoInfo"]["taskId"], task_id)
        self.assertEqual(payload["videoInfo"]["thumbnailUrl"], "https://example.com/thumb.jpg")

        listed = self.client.get("/api/resources/videos", params={"keyword": "Smart agriculture"})
        self.assertEqual(listed.status_code, 200)
        item = listed.json()["items"][0]
        self.assertEqual(item["downloadUrl"], "/api/video/files/agri.mp4")
        self.assertEqual(item["videoInfo"]["downloadStatus"], "completed")


if __name__ == "__main__":
    unittest.main()
