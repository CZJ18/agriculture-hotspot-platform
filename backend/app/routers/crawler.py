from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.crawlers.base import CrawlerAuthRequired, CrawlerError
from app.database import SessionLocal, get_db
from app.services.crawler_service import CrawlerService

router = APIRouter(prefix="/crawler", tags=["crawler"])


class CrawlerRequest(BaseModel):
    platform: str = Field(..., description="Crawler platform name, or 'all' to run every configured crawler.")
    include_hotspots: bool = Field(default=True, alias="includeHotspots")
    limit: int = Field(default=50, ge=1, le=500)


def run_crawler_request_task(request_id: int) -> None:
    db = SessionLocal()
    try:
        CrawlerService(db).run_request(request_id)
    finally:
        db.close()


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


@router.post("/request", status_code=202)
def request_crawler(payload: CrawlerRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)) -> dict:
    service = CrawlerService(db)
    platform = payload.platform.strip()
    try:
        task = service.create_request(platform, include_hotspots=payload.include_hotspots, limit=payload.limit)
        background_tasks.add_task(run_crawler_request_task, task["id"])
        return {**task, "status": "accepted"}
    except CrawlerError as exc:
        raise HTTPException(status_code=400, detail={"status": "error", "platform": platform, "message": str(exc)}) from exc


@router.get("/requests")
def list_crawler_requests(limit: int = 50, db: Session = Depends(get_db)) -> list[dict]:
    return CrawlerService(db).list_requests(limit=limit)


@router.get("/requests/{request_id}")
def get_crawler_request(request_id: int, db: Session = Depends(get_db)) -> dict:
    task = CrawlerService(db).get_request(request_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Crawler request not found.")
    return task
