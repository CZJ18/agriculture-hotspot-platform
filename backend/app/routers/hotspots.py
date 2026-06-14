from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.hotspot import HotspotRead
from app.services.crawler_service import CrawlerService

router = APIRouter(prefix="/hotspots", tags=["hotspots"])


@router.get("", response_model=list[HotspotRead])
def list_hotspots(
    platform: str | None = None,
    limit: int = Query(default=100, ge=1, le=1000),
    db: Session = Depends(get_db),
) -> list[dict]:
    return CrawlerService(db).list_hotspots(platform=platform, limit=limit)


@router.get("/platforms")
def list_platforms() -> list[str]:
    return [
        "github_trending",
        "hacker_news",
        "news_rss",
        "bilibili",
        "zhihu",
        "weibo",
        "douyin",
        "wechat_channels",
        "youtube",
    ]
