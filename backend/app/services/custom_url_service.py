from sqlalchemy import select
from sqlalchemy.orm import Session

from app.crawlers.custom_url.base import CustomUrlAdapter
from app.crawlers.custom_url.bilibili_adapter import BilibiliAdapter
from app.crawlers.custom_url.generic_adapter import GenericAdapter
from app.crawlers.custom_url.github_adapter import GitHubAdapter
from app.crawlers.custom_url.zhihu_adapter import ZhihuAdapter
from app.models.custom_url_task import CustomUrlTask
from app.security.url_validator import URLValidationError, fetch_public_text, validate_url
from app.services.ai_service import AIService
from app.services.serialization import dumps_list, loads_list


ADAPTERS: list[CustomUrlAdapter] = [GitHubAdapter(), BilibiliAdapter(), ZhihuAdapter(), GenericAdapter()]


class CustomUrlService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.ai = AIService()

    def submit(self, url: str) -> dict:
        valid = validate_url(url)
        task = CustomUrlTask(url=valid.normalized_url, domain=valid.hostname, platform=self._adapter(valid.normalized_url).platform)
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return self._to_dict(task)

    def analyze(self, url: str) -> dict:
        try:
            task_dict = self.submit(url)
        except URLValidationError as exc:
            task = CustomUrlTask(url=url, status="blocked", error_message=str(exc))
            self.db.add(task)
            self.db.commit()
            self.db.refresh(task)
            return self._to_analyze_response(task)

        task = self.db.get(CustomUrlTask, task_dict["id"])
        if task is None:
            raise RuntimeError("Task was not persisted.")
        try:
            task.status = "fetching"
            self.db.commit()
            html, final_url = fetch_public_text(task.url)
            adapter = self._adapter(final_url)
            parsed = adapter.parse(final_url, html)
            task.status = "analyzing"
            task.url = final_url
            task.domain = parsed.domain
            task.platform = parsed.platform
            task.title = parsed.title
            task.description = parsed.description
            task.content_excerpt = parsed.content_excerpt

            analysis = self.ai.analyze_text(parsed.title, " ".join(filter(None, [parsed.description, parsed.content_excerpt])))
            task.summary = analysis.summary
            task.keywords = dumps_list(analysis.keywords)
            task.sentiment = analysis.sentiment
            task.category = analysis.category
            task.trend_opinion = analysis.trend_opinion
            task.status = "completed"
            self.db.commit()
        except URLValidationError as exc:
            task.status = "blocked"
            task.error_message = str(exc)
            self.db.commit()
        except Exception as exc:  # noqa: BLE001
            task.status = "failed"
            task.error_message = str(exc)
            self.db.commit()
        self.db.refresh(task)
        return self._to_analyze_response(task)

    def list_tasks(self, limit: int = 100) -> list[dict]:
        stmt = select(CustomUrlTask).order_by(CustomUrlTask.created_at.desc()).limit(limit)
        return [self._to_dict(item) for item in self.db.execute(stmt).scalars()]

    def get_task(self, task_id: int) -> dict | None:
        task = self.db.get(CustomUrlTask, task_id)
        return self._to_dict(task) if task else None

    def _adapter(self, url: str) -> CustomUrlAdapter:
        return next(adapter for adapter in ADAPTERS if adapter.match(url))

    def _to_dict(self, task: CustomUrlTask) -> dict:
        return {
            "id": task.id,
            "url": task.url,
            "domain": task.domain,
            "platform": task.platform,
            "title": task.title,
            "description": task.description,
            "content_excerpt": task.content_excerpt,
            "summary": task.summary,
            "keywords": loads_list(task.keywords),
            "sentiment": task.sentiment,
            "category": task.category,
            "trend_opinion": task.trend_opinion,
            "status": task.status,
            "error_message": task.error_message,
            "created_at": task.created_at,
            "updated_at": task.updated_at,
        }

    def _to_analyze_response(self, task: CustomUrlTask) -> dict:
        return {
            "task_id": task.id,
            "status": task.status,
            "title": task.title,
            "platform": task.platform,
            "summary": task.summary,
            "keywords": loads_list(task.keywords),
            "sentiment": task.sentiment,
            "category": task.category,
            "trend_opinion": task.trend_opinion,
            "source_url": task.url,
        }
