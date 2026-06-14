from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.crawlers.base import CrawlerAuthRequired, CrawlerError
from app.database import get_db
from app.services.crawler_service import CrawlerService

router = APIRouter(prefix="/crawler", tags=["crawler"])


@router.post("/run")
def run_stable_crawlers(db: Session = Depends(get_db)) -> list[dict]:
    return CrawlerService(db).crawl_all_stable()


@router.post("/run/{platform}")
def run_platform(platform: str, db: Session = Depends(get_db)) -> dict:
    try:
        return CrawlerService(db).crawl_platform(platform)
    except CrawlerAuthRequired as exc:
        raise HTTPException(status_code=428, detail=exc.to_dict()) from exc
    except CrawlerError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
