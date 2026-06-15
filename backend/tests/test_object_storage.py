import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock, patch

from app.storage import ObjectStorageService


class ObjectStorageServiceTests(unittest.TestCase):
    @patch.dict(
        "os.environ",
        {
            "OBJECT_STORAGE_ENABLED": "true",
            "OBJECT_STORAGE_PROVIDER": "supabase",
            "OBJECT_STORAGE_PREFIX": "videos",
            "SUPABASE_URL": "https://project.supabase.co",
            "SUPABASE_SERVICE_ROLE_KEY": "secret",
            "SUPABASE_STORAGE_BUCKET": "agriculture-videos",
        },
    )
    @patch("app.storage.object_storage.requests.post")
    def test_supabase_upload_returns_storage_uri(self, post):
        from app.config import get_settings

        get_settings.cache_clear()
        post.return_value = Mock(status_code=200, text="{}")

        with TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "clip.mp4"
            path.write_bytes(b"video")

            uri = ObjectStorageService().upload_file(path)

        self.assertTrue(uri.startswith("supabase://agriculture-videos/videos/"))
        self.assertTrue(uri.endswith(".mp4"))
        called_url = post.call_args.args[0]
        headers = post.call_args.kwargs["headers"]
        self.assertTrue(called_url.startswith("https://project.supabase.co/storage/v1/object/agriculture-videos/videos/"))
        self.assertEqual(headers["Authorization"], "Bearer secret")
        self.assertEqual(headers["apikey"], "secret")
        self.assertEqual(headers["Content-Type"], "video/mp4")
        get_settings.cache_clear()

    @patch.dict(
        "os.environ",
        {
            "OBJECT_STORAGE_PROVIDER": "supabase",
            "SUPABASE_URL": "https://project.supabase.co",
            "SUPABASE_SERVICE_ROLE_KEY": "secret",
            "SUPABASE_STORAGE_BUCKET": "agriculture-videos",
            "SUPABASE_STORAGE_PUBLIC": "true",
        },
    )
    def test_supabase_public_download_url(self):
        from app.config import get_settings

        get_settings.cache_clear()

        url = ObjectStorageService().download_url("supabase://agriculture-videos/videos/test.mp4")

        self.assertEqual(url, "https://project.supabase.co/storage/v1/object/public/agriculture-videos/videos/test.mp4")
        get_settings.cache_clear()

    @patch.dict(
        "os.environ",
        {
            "OBJECT_STORAGE_PROVIDER": "supabase",
            "OBJECT_STORAGE_PRESIGN_SECONDS": "120",
            "SUPABASE_URL": "https://project.supabase.co",
            "SUPABASE_SERVICE_ROLE_KEY": "secret",
            "SUPABASE_STORAGE_BUCKET": "agriculture-videos",
        },
    )
    @patch("app.storage.object_storage.requests.post")
    def test_supabase_private_download_url_is_signed(self, post):
        from app.config import get_settings

        get_settings.cache_clear()
        post.return_value = Mock(status_code=200, text="{}", json=lambda: {"signedURL": "/object/sign/path?token=abc"})

        url = ObjectStorageService().download_url("supabase://agriculture-videos/videos/test.mp4")

        self.assertEqual(url, "https://project.supabase.co/storage/v1/object/sign/path?token=abc")
        called_url = post.call_args.args[0]
        self.assertEqual(
            called_url,
            "https://project.supabase.co/storage/v1/object/sign/agriculture-videos/videos/test.mp4",
        )
        self.assertEqual(post.call_args.kwargs["json"], {"expiresIn": 120})
        get_settings.cache_clear()


if __name__ == "__main__":
    unittest.main()
