from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.export_service import ExportService

router = APIRouter(prefix="/export", tags=["export"])


@router.get("/hotspots.xlsx")
def export_hotspots(platform: str | None = None, db: Session = Depends(get_db)) -> StreamingResponse:
    stream = ExportService(db).hotspots_excel(platform=platform)
    headers = {"Content-Disposition": 'attachment; filename="hotspots.xlsx"'}
    return StreamingResponse(
        stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers,
    )
