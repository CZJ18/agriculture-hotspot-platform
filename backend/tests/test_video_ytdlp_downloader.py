import unittest
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock, patch

from app.services.video_service import VideoService
from app.video.downloaders import YtDlpVideoDownloader
from app.video.parsers.base import VideoMetadata


class VideoYtDlpDownloaderTests(unittest.TestCase):
    def test_bilibili_ytdlp_headers_include_browser_context(self):
        headers = YtDlpVideoDownloader()._http_headers("https://www.bilibili.com/video/BV123/")

        self.assertIn("Chrome/", headers["User-Agent"])
        self.assertEqual(headers["Referer"], "https://www.bilibili.com/")
        self.assertEqual(headers["Origin"], "https://www.bilibili.com")

    @patch.dict("os.environ", {"VIDEO_DOWNLOAD_ENABLED": "false", "VIDEO_YTDLP_ENABLED": "false"})
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

    @patch.dict(
        "os.environ",
        {
            "OBJECT_STORAGE_ENABLED": "true",
            "OBJECT_STORAGE_BUCKET": "agriculture-videos",
            "OBJECT_STORAGE_ENDPOINT_URL": "https://example.r2.cloudflarestorage.com",
            "OBJECT_STORAGE_ACCESS_KEY_ID": "key",
            "OBJECT_STORAGE_SECRET_ACCESS_KEY": "secret",
        },
    )
    @patch("app.services.video_service.ObjectStorageService")
    def test_object_storage_upload_removes_local_file(self, storage_cls):
        from app.config import get_settings

        get_settings.cache_clear()
        storage = Mock()
        storage.enabled.return_value = True
        storage.upload_file.return_value = "r2://agriculture-videos/videos/test.mp4"
        storage_cls.return_value = storage

        with TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "test.mp4"
            path.write_bytes(b"video")

            persisted = VideoService(db=Mock())._persist_download(path)

            self.assertEqual(persisted, "r2://agriculture-videos/videos/test.mp4")
            storage.upload_file.assert_called_once_with(path)
            self.assertFalse(path.exists())

        get_settings.cache_clear()

    @patch.dict(
        "os.environ",
        {
            "OBJECT_STORAGE_ENABLED": "true",
            "OBJECT_STORAGE_BUCKET": "agriculture-videos",
            "OBJECT_STORAGE_ENDPOINT_URL": "https://example.r2.cloudflarestorage.com",
            "OBJECT_STORAGE_ACCESS_KEY_ID": "key",
            "OBJECT_STORAGE_SECRET_ACCESS_KEY": "secret",
        },
    )
    @patch("app.services.video_service.ObjectStorageService")
    def test_remote_download_path_returns_object_storage_url(self, storage_cls):
        from app.config import get_settings

        get_settings.cache_clear()
        storage = Mock()
        storage.is_storage_uri.return_value = True
        storage.download_url.return_value = "https://cdn.example.com/videos/test.mp4"
        storage_cls.return_value = storage

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
        task.download_path = "r2://agriculture-videos/videos/test.mp4"
        task.status = "completed"
        task.error_message = None
        task.created_at = datetime.utcnow()
        task.updated_at = datetime.utcnow()

        payload = VideoService(db=Mock())._to_dict(task)

        self.assertEqual(payload["download_url"], "https://cdn.example.com/videos/test.mp4")
        storage.download_url.assert_called_once_with("r2://agriculture-videos/videos/test.mp4")
        get_settings.cache_clear()


if __name__ == "__main__":
    unittest.main()
