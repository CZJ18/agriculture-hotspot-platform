from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.custom_url import (
    CustomUrlAnalyzeRequest,
    CustomUrlAnalyzeResponse,
    CustomUrlSubmit,
    CustomUrlTaskRead,
)
from app.security.url_validator import URLValidationError
from app.security.rate_limit import enforce_rate_limit
from app.services.custom_url_service import CustomUrlService

router = APIRouter(prefix="/custom-url", tags=["custom-url"])


@router.post("/submit", response_model=CustomUrlTaskRead)
def submit(payload: CustomUrlSubmit, request: Request, db: Session = Depends(get_db)) -> dict:
    enforce_rate_limit(request)
    try:
        return CustomUrlService(db).submit(str(payload.url))
    except URLValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/tasks", response_model=list[CustomUrlTaskRead])
def list_tasks(db: Session = Depends(get_db)) -> list[dict]:
    return CustomUrlService(db).list_tasks()


@router.get("/tasks/{task_id}", response_model=CustomUrlTaskRead)
def get_task(task_id: int, db: Session = Depends(get_db)) -> dict:
    task = CustomUrlService(db).get_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found.")
    return task


@router.post("/analyze", response_model=CustomUrlAnalyzeResponse)
def analyze(payload: CustomUrlAnalyzeRequest, request: Request, db: Session = Depends(get_db)) -> dict:
    enforce_rate_limit(request)
    return CustomUrlService(db).analyze(str(payload.url))
