from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.schemas.video import VideoParseRequest, VideoTaskRead
from app.security.rate_limit import enforce_rate_limit
from app.services.video_service import VideoService

router = APIRouter(prefix="/video", tags=["video"])


@router.post("/parse", response_model=VideoTaskRead)
def parse_video(payload: VideoParseRequest, request: Request, db: Session = Depends(get_db)) -> dict:
    enforce_rate_limit(request)
    return VideoService(db).parse(str(payload.url), download=payload.download)


@router.get("/tasks", response_model=list[VideoTaskRead])
def list_video_tasks(db: Session = Depends(get_db)) -> list[dict]:
    return VideoService(db).list_tasks()


@router.get("/tasks/{task_id}", response_model=VideoTaskRead)
def get_video_task(task_id: int, db: Session = Depends(get_db)) -> dict:
    task = VideoService(db).get_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Video task not found.")
    return task


@router.get("/files/{filename}")
def get_video_file(filename: str):
    base_dir = Path(get_settings().video_download_dir).resolve()
    path = (base_dir / filename).resolve()
    if base_dir not in path.parents or not path.exists():
        raise HTTPException(status_code=404, detail="Video file not found.")
    return FileResponse(path)
