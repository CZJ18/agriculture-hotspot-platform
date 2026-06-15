import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch

from app.services.video_service import VideoService
from app.video.parsers.base import VideoMetadata


class VideoYtDlpDownloaderTests(unittest.TestCase):
    @patch.dict("os.environ", {"VIDEO_YTDLP_ENABLED": "true"})
    @patch("app.services.video_service.YtDlpVideoDownloader")
    def test_platform_download_uses_ytdlp_when_no_direct_video_url(self, downloader_cls):
        from app.config import get_settings

        get_settings.cache_clear()
        downloader = Mock()
        downloader.download.return_value = Path("downloads/videos/test.mp4")
        downloader_cls.return_value = downloader

        task = Mock()
        task.download_status = "pending"
        task.error_message = None
        metadata = VideoMetadata(
            source_url="https://www.bilibili.com/video/BV123",
            final_url="https://www.bilibili.com/video/BV123",
            platform="bilibili",
            title="Bilibili video",
        )

        service = VideoService(db=Mock())
        service._maybe_download(task, metadata)

        downloader.download.assert_called_once_with(metadata.final_url)
        self.assertEqual(task.download_status, "completed")
        self.assertEqual(task.download_path, "downloads\\videos\\test.mp4")

    def test_completed_download_returns_public_file_url(self):
        task = Mock()
        task.id = 1
        task.url = "https://example.com/video.mp4"
        task.final_url = "https://example.com/video.mp4"
        task.platform = "direct_video"
        task.title = "video"
        task.author = None
        task.description = None
        task.thumbnail_url = None
        task.duration = None
        task.published_at = None
        task.view_count = None
        task.direct_video_url = "https://example.com/video.mp4"
        task.download_requested = True
        task.download_status = "completed"
        task.download_path = "downloads/videos/test.mp4"
        task.status = "completed"
        task.error_message = None
        task.created_at = datetime.utcnow()
        task.updated_at = datetime.utcnow()

        payload = VideoService(db=Mock())._to_dict(task)

        self.assertEqual(payload["download_url"], "/api/video/files/test.mp4")


if __name__ == "__main__":
    unittest.main()
