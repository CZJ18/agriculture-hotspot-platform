from datetime import date, datetime

from sqlalchemy import Date, DateTime, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class DailyAnalysis(Base):
    __tablename__ = "daily_analysis"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    date: Mapped[date] = mapped_column(Date, index=True, unique=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    keywords: Mapped[str | None] = mapped_column(Text, nullable=True)
    sentiment_overview: Mapped[str | None] = mapped_column(Text, nullable=True)
    trend_opinion: Mapped[str | None] = mapped_column(Text, nullable=True)
    platform_comparison: Mapped[str | None] = mapped_column(Text, nullable=True)
    content_suggestions: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
