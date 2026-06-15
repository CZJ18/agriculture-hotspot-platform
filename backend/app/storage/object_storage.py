from __future__ import annotations

import mimetypes
from pathlib import Path
from urllib.parse import quote, urljoin
from uuid import uuid4

import requests

from app.config import get_settings


class ObjectStorageError(RuntimeError):
    pass


class ObjectStorageService:
    s3_uri_scheme = "r2"
    supabase_uri_scheme = "supabase"

    def __init__(self) -> None:
        self.settings = get_settings()

    def enabled(self) -> bool:
        return self.settings.object_storage_enabled

    def upload_file(self, path: Path, content_type: str | None = None) -> str:
        provider = self._provider()
        if not path.exists() or not path.is_file():
            raise ObjectStorageError(f"File does not exist: {path}")

        key = self._object_key(path)
        final_content_type = content_type or mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        if provider == "supabase":
            return self._upload_supabase_file(path, key, final_content_type)
        return self._upload_s3_file(path, key, final_content_type)

    def download_url(self, storage_uri: str) -> str:
        provider, key = self._parse_storage_uri(storage_uri)
        if provider == "supabase":
            return self._supabase_download_url(key)

        public_base = self.settings.object_storage_public_base_url.strip()
        if public_base:
            return f"{public_base.rstrip('/')}/{quote(key, safe='/')}"
        return self._s3_client().generate_presigned_url(
            "get_object",
            Params={"Bucket": self.settings.object_storage_bucket, "Key": key},
            ExpiresIn=self.settings.object_storage_presign_seconds,
        )

    def storage_uri(self, key: str) -> str:
        if self._provider() == "supabase":
            return f"{self.supabase_uri_scheme}://{self.settings.supabase_storage_bucket}/{key.lstrip('/')}"
        return f"{self.s3_uri_scheme}://{self.settings.object_storage_bucket}/{key.lstrip('/')}"

    def is_storage_uri(self, value: str | None) -> bool:
        return bool(value and (value.startswith(f"{self.s3_uri_scheme}://") or value.startswith(f"{self.supabase_uri_scheme}://")))

    def key_from_uri(self, storage_uri: str) -> str:
        return self._parse_storage_uri(storage_uri)[1]

    def _object_key(self, path: Path) -> str:
        prefix = self.settings.object_storage_prefix.strip("/")
        suffix = path.suffix.lower() or ".bin"
        filename = f"{uuid4().hex}{suffix}"
        return f"{prefix}/{filename}" if prefix else filename

    def _validate_settings(self) -> None:
        if self._provider() == "supabase":
            self._validate_supabase_settings()
            return

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

    def _validate_supabase_settings(self) -> None:
        missing = [
            name
            for name, value in {
                "SUPABASE_URL": self.settings.supabase_url,
                "SUPABASE_SERVICE_ROLE_KEY": self.settings.supabase_service_role_key,
                "SUPABASE_STORAGE_BUCKET": self.settings.supabase_storage_bucket,
            }.items()
            if not value
        ]
        if missing:
            raise ObjectStorageError(f"Missing Supabase storage settings: {', '.join(missing)}")

    def _upload_s3_file(self, path: Path, key: str, content_type: str) -> str:
        self._validate_settings()
        extra_args = {"ContentType": content_type}
        self._s3_client().upload_file(str(path), self.settings.object_storage_bucket, key, ExtraArgs=extra_args)
        return self.storage_uri(key)

    def _upload_supabase_file(self, path: Path, key: str, content_type: str) -> str:
        self._validate_supabase_settings()
        url = self._supabase_url(f"/storage/v1/object/{self.settings.supabase_storage_bucket}/{quote(key, safe='/')}")
        headers = self._supabase_headers()
        headers.update({"Content-Type": content_type, "x-upsert": "false", "cache-control": "3600"})
        with path.open("rb") as file:
            response = requests.post(url, headers=headers, data=file, timeout=self.settings.request_timeout_seconds)
        if response.status_code >= 400:
            raise ObjectStorageError(f"Supabase upload failed: HTTP {response.status_code} {response.text[:300]}")
        return self.storage_uri(key)

    def _supabase_download_url(self, key: str) -> str:
        if self.settings.supabase_storage_public:
            return self._supabase_url(
                f"/storage/v1/object/public/{self.settings.supabase_storage_bucket}/{quote(key, safe='/')}"
            )

        url = self._supabase_url(f"/storage/v1/object/sign/{self.settings.supabase_storage_bucket}/{quote(key, safe='/')}")
        response = requests.post(
            url,
            headers={**self._supabase_headers(), "Content-Type": "application/json"},
            json={"expiresIn": self.settings.object_storage_presign_seconds},
            timeout=self.settings.request_timeout_seconds,
        )
        if response.status_code >= 400:
            raise ObjectStorageError(f"Supabase signed URL failed: HTTP {response.status_code} {response.text[:300]}")
        payload = response.json()
        signed_url = payload.get("signedURL") or payload.get("signedUrl") or payload.get("signed_url")
        if not signed_url:
            raise ObjectStorageError("Supabase signed URL response did not include a signed URL.")
        return signed_url if signed_url.startswith("http") else self._supabase_url(signed_url)

    def _parse_storage_uri(self, storage_uri: str) -> tuple[str, str]:
        s3_prefix = f"{self.s3_uri_scheme}://{self.settings.object_storage_bucket}/"
        if storage_uri.startswith(s3_prefix):
            return "s3", storage_uri[len(s3_prefix) :]

        supabase_prefix = f"{self.supabase_uri_scheme}://{self.settings.supabase_storage_bucket}/"
        if storage_uri.startswith(supabase_prefix):
            return "supabase", storage_uri[len(supabase_prefix) :]

        raise ObjectStorageError("Object storage URI does not match configured bucket.")

    def _supabase_url(self, path: str) -> str:
        return urljoin(self.settings.supabase_url.rstrip("/") + "/", path.lstrip("/"))

    def _supabase_headers(self) -> dict[str, str]:
        key = self.settings.supabase_service_role_key
        return {"apikey": key, "Authorization": f"Bearer {key}"}

    def _provider(self) -> str:
        provider = self.settings.object_storage_provider.lower().strip()
        if provider in {"r2", "s3"}:
            return "s3"
        if provider == "supabase":
            return "supabase"
        raise ObjectStorageError(f"Unsupported OBJECT_STORAGE_PROVIDER: {self.settings.object_storage_provider!r}")

    def _s3_client(self):
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
