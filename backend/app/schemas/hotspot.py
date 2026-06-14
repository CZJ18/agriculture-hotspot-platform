from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class HotspotBase(BaseModel):
    platform: str
    rank: int | None = None
    title: str
    url: str
    heat: str | None = None
    category: str | None = None
    author: str | None = None
    summary: str | None = None
    sentiment: str | None = None
    keywords: list[str] = Field(default_factory=list)
    captured_at: datetime | None = None


class HotspotCreate(HotspotBase):
    pass


class HotspotRead(HotspotBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
