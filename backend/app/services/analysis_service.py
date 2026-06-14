from datetime import date, datetime, time

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.analysis import DailyAnalysis
from app.models.hotspot import Hotspot
from app.services.ai_service import AIService
from app.services.serialization import dumps_list, loads_list


class AnalysisService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.ai = AIService()

    def analyze_daily(self, target_date: date | None = None) -> dict:
        target_date = target_date or date.today()
        day_start = datetime.combine(target_date, time.min)
        day_end = datetime.combine(target_date, time.max)
        stmt = select(Hotspot).where(Hotspot.captured_at >= day_start, Hotspot.captured_at <= day_end).order_by(Hotspot.rank.asc())
        hotspots = list(self.db.execute(stmt).scalars())
        result = self.ai.summarize_daily([item.title for item in hotspots])

        record = self.db.execute(select(DailyAnalysis).where(DailyAnalysis.date == target_date)).scalar_one_or_none()
        if record is None:
            record = DailyAnalysis(date=target_date)
            self.db.add(record)
        record.summary = str(result["summary"])
        record.keywords = dumps_list(result["keywords"])  # type: ignore[arg-type]
        record.sentiment_overview = str(result["sentiment_overview"])
        record.trend_opinion = str(result["trend_opinion"])
        record.platform_comparison = str(result["platform_comparison"])
        record.content_suggestions = str(result["content_suggestions"])
        self.db.commit()
        self.db.refresh(record)
        return self._to_dict(record)

    def latest(self) -> dict | None:
        record = self.db.execute(select(DailyAnalysis).order_by(DailyAnalysis.date.desc())).scalars().first()
        return self._to_dict(record) if record else None

    def _to_dict(self, record: DailyAnalysis) -> dict:
        return {
            "id": record.id,
            "date": record.date,
            "summary": record.summary,
            "keywords": loads_list(record.keywords),
            "sentiment_overview": record.sentiment_overview,
            "trend_opinion": record.trend_opinion,
            "platform_comparison": record.platform_comparison,
            "content_suggestions": record.content_suggestions,
            "created_at": record.created_at,
            "updated_at": record.updated_at,
        }
