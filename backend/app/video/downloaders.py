from pathlib import Path
from urllib.parse import urlparse
from uuid import uuid4

from app.config import get_settings
from app.security.url_validator import URLValidationError, validate_url


class VideoDownloadError(RuntimeError):
    pass


class YtDlpVideoDownloader:
    def __init__(self) -> None:
        self.settings = get_settings()

    def download(self, url: str) -> Path:
        self._validate_source(url)
        try:
            from yt_dlp import YoutubeDL
        except ImportError as exc:
            raise VideoDownloadError("yt-dlp is not installed. Install backend requirements first.") from exc

        download_dir = Path(self.settings.video_download_dir)
        download_dir.mkdir(parents=True, exist_ok=True)
        output_template = str(download_dir / f"{uuid4().hex}.%(ext)s")
        options = {
            "outtmpl": output_template,
            "format": "b[ext=mp4]/best[ext=mp4]/best",
            "merge_output_format": "mp4",
            "noplaylist": True,
            "max_filesize": self.settings.video_max_download_bytes,
            "quiet": True,
            "no_warnings": True,
            "restrictfilenames": True,
            "continuedl": False,
            "overwrites": False,
            "http_headers": self._http_headers(url),
        }
        if self.settings.video_ytdlp_cookie_file:
            cookie_path = Path(self.settings.video_ytdlp_cookie_file)
            if not cookie_path.exists():
                raise VideoDownloadError("Configured VIDEO_YTDLP_COOKIE_FILE does not exist.")
            options["cookiefile"] = str(cookie_path)

        before = set(download_dir.glob("*"))
        with YoutubeDL(options) as ydl:
            ydl.download([url])
        created = [path for path in download_dir.glob("*") if path not in before and path.is_file()]
        if not created:
            raise VideoDownloadError("yt-dlp finished but no output file was found.")

        path = max(created, key=lambda item: item.stat().st_mtime)
        if path.stat().st_size > self.settings.video_max_download_bytes:
            path.unlink(missing_ok=True)
            raise URLValidationError("Video file exceeds VIDEO_MAX_DOWNLOAD_BYTES.")
        return path

    def _validate_source(self, url: str) -> None:
        valid = validate_url(url, resolve_dns=True)
        host = (urlparse(valid.normalized_url).hostname or "").lower()
        allowed = [domain.lower() for domain in self.settings.video_ytdlp_allowed_domains]
        if not any(host == domain or host.endswith(f".{domain}") for domain in allowed):
            raise URLValidationError(f"yt-dlp downloads are not allowed for host {host!r}.")

    def _http_headers(self, url: str) -> dict[str, str]:
        host = (urlparse(url).hostname or "").lower()
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/126.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        }
        if host == "bilibili.com" or host.endswith(".bilibili.com"):
            headers["Referer"] = "https://www.bilibili.com/"
            headers["Origin"] = "https://www.bilibili.com"
        elif host == "youtube.com" or host.endswith(".youtube.com") or host == "youtu.be":
            headers["Referer"] = "https://www.youtube.com/"
            headers["Origin"] = "https://www.youtube.com"
        return headers
