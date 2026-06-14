from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.analysis import DailyAnalysisRead, DailyAnalysisRequest
from app.services.analysis_service import AnalysisService

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.post("/daily", response_model=DailyAnalysisRead)
def analyze_daily(payload: DailyAnalysisRequest, db: Session = Depends(get_db)) -> dict:
    return AnalysisService(db).analyze_daily(payload.date)


@router.get("/latest", response_model=DailyAnalysisRead)
def latest_analysis(db: Session = Depends(get_db)) -> dict:
    result = AnalysisService(db).latest()
    if result is None:
        raise HTTPException(status_code=404, detail="No analysis found.")
    return result
