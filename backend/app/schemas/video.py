from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, HttpUrl


class VideoParseRequest(BaseModel):
    url: HttpUrl
    download: bool = False


class VideoTaskRead(BaseModel):
    id: int
    url: str
    final_url: str | None = None
    platform: str | None = None
    title: str | None = None
    author: str | None = None
    description: str | None = None
    thumbnail_url: str | None = None
    duration: str | None = None
    published_at: str | None = None
    view_count: str | None = None
    direct_video_url: str | None = None
    download_requested: bool
    download_status: str
    download_path: str | None = None
    status: str
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
