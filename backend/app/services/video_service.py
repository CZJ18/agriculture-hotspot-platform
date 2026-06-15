from pathlib import Path
from urllib.parse import unquote, urlparse
from uuid import uuid4

import requests
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.video_task import VideoTask
from app.security.url_validator import URLValidationError, fetch_public_text, validate_url
from app.storage import ObjectStorageService
from app.video.parsers import BilibiliVideoParser, GenericVideoParser, YouTubeVideoParser
from app.video.parsers.base import VideoMetadata, VideoParser
from app.video.downloaders import YtDlpVideoDownloader


VIDEO_PARSERS: list[VideoParser] = [YouTubeVideoParser(), BilibiliVideoParser(), GenericVideoParser()]
ALLOWED_VIDEO_TYPES = {"video/mp4": ".mp4", "video/webm": ".webm", "video/quicktime": ".mov"}


class VideoService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.settings = get_settings()

    def parse(self, url: str, download: bool = False) -> dict:
        task = VideoTask(url=url, download_requested=download, download_status="pending" if download else "not_requested")
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)

        try:
            task.status = "fetching"
            self.db.commit()
            direct_metadata = self._direct_video_metadata(url)
            if direct_metadata:
                metadata = direct_metadata
            else:
                html, final_url = fetch_public_text(url)
                parser = self._parser(final_url)
                metadata = parser.parse(final_url, html)
                metadata.source_url = url
                metadata.final_url = final_url
            self._apply_metadata(task, metadata)

            if download:
                self._maybe_download(task, metadata)
            task.status = "completed"
            self.db.commit()
        except URLValidationError as exc:
            task.status = "blocked"
            task.download_status = "blocked" if download else task.download_status
            task.error_message = str(exc)
            self.db.commit()
        except Exception as exc:  # noqa: BLE001
            task.status = "failed"
            task.download_status = "failed" if download else task.download_status
            task.error_message = str(exc)
            self.db.commit()

        self.db.refresh(task)
        return self._to_dict(task)

    def list_tasks(self, limit: int = 100) -> list[dict]:
        stmt = select(VideoTask).order_by(VideoTask.created_at.desc()).limit(limit)
        return [self._to_dict(item) for item in self.db.execute(stmt).scalars()]

    def get_task(self, task_id: int) -> dict | None:
        task = self.db.get(VideoTask, task_id)
        return self._to_dict(task) if task else None

    def _parser(self, url: str) -> VideoParser:
        return next(parser for parser in VIDEO_PARSERS if parser.match(url))

    def _direct_video_metadata(self, url: str) -> VideoMetadata | None:
        parsed = urlparse(url)
        suffix = Path(parsed.path).suffix.lower()
        if suffix not in {".mp4", ".webm", ".mov"}:
            return None
        valid = validate_url(url, resolve_dns=True)
        filename = unquote(Path(parsed.path).name) or "video"
        return VideoMetadata(
            source_url=url,
            final_url=valid.normalized_url,
            platform="direct_video",
            title=filename,
            direct_video_url=valid.normalized_url,
        )

    def _apply_metadata(self, task: VideoTask, metadata: VideoMetadata) -> None:
        task.final_url = metadata.final_url
        task.platform = metadata.platform
        task.title = metadata.title
        task.author = metadata.author
        task.description = metadata.description
        task.thumbnail_url = metadata.thumbnail_url
        task.duration = metadata.duration
        task.published_at = metadata.published_at
        task.view_count = metadata.view_count
        task.direct_video_url = metadata.direct_video_url

    def _maybe_download(self, task: VideoTask, metadata: VideoMetadata) -> None:
        if not metadata.direct_video_url:
            task.download_path = str(self._persist_download(YtDlpVideoDownloader().download(metadata.final_url)))
            task.download_status = "completed"
            return
        task.download_path = str(self._persist_download(self._download_direct_video(metadata.direct_video_url)))
        task.download_status = "completed"

    def _persist_download(self, path: Path) -> Path | str:
        storage = ObjectStorageService()
        if not storage.enabled():
            return path

        storage_uri = storage.upload_file(path)
        if self.settings.object_storage_delete_local_after_upload:
            path.unlink(missing_ok=True)
        return storage_uri

    def _download_direct_video(self, url: str) -> Path:
        current = validate_url(url, resolve_dns=True).normalized_url
        session = requests.Session()
        response = None
        for _ in range(self.settings.max_redirects + 1):
            response = session.get(current, timeout=self.settings.request_timeout_seconds, stream=True, allow_redirects=False)
            if response.is_redirect:
                location = response.headers.get("Location")
                if not location:
                    raise URLValidationError("Redirect target is missing.")
                current = requests.compat.urljoin(current, location)
                current = validate_url(current, resolve_dns=True).normalized_url
                continue
            break
        if response is None or response.is_redirect:
            raise URLValidationError("Too many redirects.")
        response.raise_for_status()
        content_type = response.headers.get("Content-Type", "").split(";")[0].lower()
        extension = ALLOWED_VIDEO_TYPES.get(content_type)
        if not extension:
            raise URLValidationError(f"Only public direct video files are downloadable, got content type {content_type!r}.")

        download_dir = Path(self.settings.video_download_dir)
        download_dir.mkdir(parents=True, exist_ok=True)
        filename = f"{uuid4().hex}{extension}"
        path = download_dir / filename

        size = 0
        with path.open("wb") as file:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if not chunk:
                    continue
                size += len(chunk)
                if size > self.settings.video_max_download_bytes:
                    file.close()
                    path.unlink(missing_ok=True)
                    raise URLValidationError("Video file exceeds VIDEO_MAX_DOWNLOAD_BYTES.")
                file.write(chunk)
        return path

    def _to_dict(self, task: VideoTask) -> dict:
        download_url = None
        if task.download_path and task.download_status == "completed":
            storage = ObjectStorageService()
            if storage.is_storage_uri(task.download_path):
                download_url = storage.download_url(task.download_path)
            else:
                download_url = f"/api/video/files/{Path(task.download_path).name}"
        return {
            "id": task.id,
            "url": task.url,
            "final_url": task.final_url,
            "platform": task.platform,
            "title": task.title,
            "author": task.author,
            "description": task.description,
            "thumbnail_url": task.thumbnail_url,
            "duration": task.duration,
            "published_at": task.published_at,
            "view_count": task.view_count,
            "direct_video_url": task.direct_video_url,
            "download_requested": task.download_requested,
            "download_status": task.download_status,
            "download_path": task.download_path,
            "download_url": download_url,
            "status": task.status,
            "error_message": task.error_message,
            "created_at": task.created_at,
            "updated_at": task.updated_at,
        }
