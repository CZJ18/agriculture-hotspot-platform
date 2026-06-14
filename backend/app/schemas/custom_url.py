from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class CustomUrlSubmit(BaseModel):
    url: HttpUrl


class CustomUrlAnalyzeRequest(BaseModel):
    url: HttpUrl


class CustomUrlTaskRead(BaseModel):
    id: int
    url: str
    domain: str | None = None
    platform: str | None = None
    title: str | None = None
    description: str | None = None
    content_excerpt: str | None = None
    summary: str | None = None
    keywords: list[str] = Field(default_factory=list)
    sentiment: str | None = None
    category: str | None = None
    trend_opinion: str | None = None
    status: str
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CustomUrlAnalyzeResponse(BaseModel):
    task_id: int
    status: str
    title: str | None = None
    platform: str | None = None
    summary: str | None = None
    keywords: list[str] = Field(default_factory=list)
    sentiment: str | None = None
    category: str | None = None
    trend_opinion: str | None = None
    source_url: str
