from __future__ import annotations

import mimetypes
from pathlib import Path
from urllib.parse import quote
from uuid import uuid4

from app.config import get_settings


class ObjectStorageError(RuntimeError):
    pass


class ObjectStorageService:
    uri_scheme = "r2"

    def __init__(self) -> None:
        self.settings = get_settings()

    def enabled(self) -> bool:
        return self.settings.object_storage_enabled

    def upload_file(self, path: Path, content_type: str | None = None) -> str:
        self._validate_settings()
        if not path.exists() or not path.is_file():
            raise ObjectStorageError(f"File does not exist: {path}")

        key = self._object_key(path)
        extra_args = {
            "ContentType": content_type or mimetypes.guess_type(path.name)[0] or "application/octet-stream",
        }
        self._client().upload_file(str(path), self.settings.object_storage_bucket, key, ExtraArgs=extra_args)
        return self.storage_uri(key)

    def download_url(self, storage_uri: str) -> str:
        key = self.key_from_uri(storage_uri)
        public_base = self.settings.object_storage_public_base_url.strip()
        if public_base:
            return f"{public_base.rstrip('/')}/{quote(key, safe='/')}"
        return self._client().generate_presigned_url(
            "get_object",
            Params={"Bucket": self.settings.object_storage_bucket, "Key": key},
            ExpiresIn=self.settings.object_storage_presign_seconds,
        )

    def storage_uri(self, key: str) -> str:
        return f"{self.uri_scheme}://{self.settings.object_storage_bucket}/{key.lstrip('/')}"

    def is_storage_uri(self, value: str | None) -> bool:
        return bool(value and value.startswith(f"{self.uri_scheme}://"))

    def key_from_uri(self, storage_uri: str) -> str:
        prefix = f"{self.uri_scheme}://{self.settings.object_storage_bucket}/"
        if not storage_uri.startswith(prefix):
            raise ObjectStorageError("Object storage URI does not match configured bucket.")
        return storage_uri[len(prefix) :]

    def _object_key(self, path: Path) -> str:
        prefix = self.settings.object_storage_prefix.strip("/")
        suffix = path.suffix.lower() or ".bin"
        filename = f"{uuid4().hex}{suffix}"
        return f"{prefix}/{filename}" if prefix else filename

    def _validate_settings(self) -> None:
        missing = [
            name
            for name, value in {
                "OBJECT_STORAGE_BUCKET": self.settings.object_storage_bucket,
                "OBJECT_STORAGE_ENDPOINT_URL": self.settings.object_storage_endpoint_url,
                "OBJECT_STORAGE_ACCESS_KEY_ID": self.settings.object_storage_access_key_id,
                "OBJECT_STORAGE_SECRET_ACCESS_KEY": self.settings.object_storage_secret_access_key,
            }.items()
            if not value
        ]
        if missing:
            raise ObjectStorageError(f"Missing object storage settings: {', '.join(missing)}")

    def _client(self):
        try:
            import boto3
        except ImportError as exc:
            raise ObjectStorageError("boto3 is not installed. Install backend requirements first.") from exc

        return boto3.client(
            "s3",
            endpoint_url=self.settings.object_storage_endpoint_url,
            aws_access_key_id=self.settings.object_storage_access_key_id,
            aws_secret_access_key=self.settings.object_storage_secret_access_key,
            region_name=self.settings.object_storage_region,
        )
