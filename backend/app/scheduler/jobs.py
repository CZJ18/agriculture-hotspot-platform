from apscheduler.schedulers.background import BackgroundScheduler

from app.database import SessionLocal
from app.services.analysis_service import AnalysisService
from app.services.crawler_service import CrawlerService
from app.utils.logger import get_logger

logger = get_logger(__name__)


def crawl_and_analyze() -> None:
    db = SessionLocal()
    try:
        CrawlerService(db).crawl_all_stable()
        AnalysisService(db).analyze_daily()
    except Exception as exc:  # noqa: BLE001
        logger.exception("Scheduled job failed: %s", exc)
    finally:
        db.close()


def build_scheduler() -> BackgroundScheduler:
    scheduler = BackgroundScheduler(timezone="UTC")
    scheduler.add_job(crawl_and_analyze, "interval", hours=6, id="crawl_and_analyze", replace_existing=True)
    return scheduler
