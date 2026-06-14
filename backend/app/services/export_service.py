from io import BytesIO

from openpyxl import Workbook
from sqlalchemy.orm import Session

from app.services.crawler_service import CrawlerService


class ExportService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def hotspots_excel(self, platform: str | None = None) -> BytesIO:
        rows = CrawlerService(self.db).list_hotspots(platform=platform, limit=1000)
        wb = Workbook()
        ws = wb.active
        ws.title = "hotspots"
        headers = ["id", "platform", "rank", "title", "url", "heat", "category", "author", "captured_at"]
        ws.append(headers)
        for row in rows:
            ws.append([row.get(header) for header in headers])
        stream = BytesIO()
        wb.save(stream)
        stream.seek(0)
        return stream
