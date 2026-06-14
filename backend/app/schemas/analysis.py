from __future__ import annotations

from datetime import date as DateType, datetime

from pydantic import BaseModel, ConfigDict, Field


class DailyAnalysisRead(BaseModel):
    id: int
    date: DateType
    summary: str | None = None
    keywords: list[str] = Field(default_factory=list)
    sentiment_overview: str | None = None
    trend_opinion: str | None = None
    platform_comparison: str | None = None
    content_suggestions: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DailyAnalysisRequest(BaseModel):
    date: DateType | None = None
