import json
from datetime import datetime

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.resource import (
    ResourceCategory,
    ResourceNotification,
    ResourceTopic,
    ResourceTopicVideo,
    ResourceVideo,
)
from app.models.video_task import VideoTask
from app.services.video_service import VideoService


class ResourceInputError(ValueError):
    pass


class ResourceService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_videos(
        self,
        keyword: str | None = None,
        category: str | None = None,
        source: str | None = None,
        topic_id: int | None = None,
        favorite: bool | None = None,
        sort: str = "latest",
    ) -> dict:
        stmt = select(ResourceVideo)
        if keyword:
            stmt = stmt.where(ResourceVideo.title.contains(keyword) | ResourceVideo.description.contains(keyword))
        if category:
            stmt = stmt.where(ResourceVideo.category == category)
        if source:
            stmt = stmt.where(ResourceVideo.source == source)
        if favorite is not None:
            stmt = stmt.where(ResourceVideo.favorite == favorite)
        videos = list(self.db.execute(stmt).scalars())
        if topic_id is not None:
            ids = {
                row.video_id
                for row in self.db.execute(select(ResourceTopicVideo).where(ResourceTopicVideo.topic_id == topic_id)).scalars()
            }
            videos = [video for video in videos if video.id in ids]

        if sort == "favorite":
            videos.sort(key=lambda item: (not item.favorite, item.created_at), reverse=False)
        elif sort == "hot":
            videos.sort(key=lambda item: self._views_number(item.views), reverse=True)
        else:
            videos.sort(key=lambda item: item.created_at, reverse=True)
        return {"items": [self.video_to_dict(item) for item in videos], "total": len(videos)}

    def create_video(self, payload: dict) -> dict:
        payload = self._with_video_task_defaults(payload)
        if not payload.get("sourceUrl"):
            raise ResourceInputError("sourceUrl or a valid videoTaskId is required.")

        video = ResourceVideo(
            title=payload.get("title") or payload["sourceUrl"],
            source=payload.get("source", "项目组"),
            source_url=payload["sourceUrl"],
            category=payload.get("category", "未分类"),
            tags=json.dumps(payload.get("tags") or [], ensure_ascii=False),
            description=payload.get("description", ""),
            cover=payload.get("cover", ""),
            duration=payload.get("duration", ""),
            views=str(payload.get("views", 0)),
            favorite=bool(payload.get("favorite", False)),
            notes=payload.get("notes"),
        )
        self.db.add(video)
        self.db.commit()
        self.db.refresh(video)
        return self.video_to_dict(video)

    def update_video(self, video_id: int, payload: dict) -> dict | None:
        video = self.db.get(ResourceVideo, video_id)
        if not video:
            return None
        payload = self._with_video_task_defaults(payload)
        field_map = {
            "title": "title",
            "source": "source",
            "sourceUrl": "source_url",
            "category": "category",
            "description": "description",
            "cover": "cover",
            "duration": "duration",
            "views": "views",
            "favorite": "favorite",
            "notes": "notes",
        }
        for incoming, attr in field_map.items():
            if incoming in payload:
                setattr(video, attr, payload[incoming])
        if "tags" in payload:
            video.tags = json.dumps(payload.get("tags") or [], ensure_ascii=False)
        self.db.commit()
        self.db.refresh(video)
        return self.video_to_dict(video)

    def delete_video(self, video_id: int) -> bool:
        video = self.db.get(ResourceVideo, video_id)
        if not video:
            return False
        self.db.delete(video)
        self.db.execute(delete(ResourceTopicVideo).where(ResourceTopicVideo.video_id == video_id))
        self.db.commit()
        return True

    def set_favorite(self, video_id: int, favorite: bool) -> dict | None:
        return self.update_video(video_id, {"favorite": favorite})

    def save_notes(self, video_id: int, notes: str) -> dict | None:
        return self.update_video(video_id, {"notes": notes})

    def list_categories(self) -> list[dict]:
        rows = self.db.execute(select(ResourceCategory).order_by(ResourceCategory.order.asc(), ResourceCategory.id.asc())).scalars()
        return [self.category_to_dict(row) for row in rows]

    def create_category(self, payload: dict) -> dict:
        category = ResourceCategory(
            name=payload["name"],
            parent=payload.get("parent"),
            icon=payload.get("icon", ""),
            order=int(payload.get("order", 0)),
            status=payload.get("status", "启用"),
            description=payload.get("description", ""),
        )
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        return self.category_to_dict(category)

    def update_category(self, category_id: int, payload: dict) -> dict | None:
        category = self.db.get(ResourceCategory, category_id)
        if not category:
            return None
        for field in ["name", "parent", "icon", "order", "status", "description"]:
            if field in payload:
                setattr(category, field, payload[field])
        self.db.commit()
        self.db.refresh(category)
        return self.category_to_dict(category)

    def delete_category(self, category_id: int) -> bool:
        category = self.db.get(ResourceCategory, category_id)
        if not category:
            return False
        self.db.delete(category)
        self.db.commit()
        return True

    def category_tree(self) -> list[dict]:
        categories = self.list_categories()
        by_name = {item["name"]: {**item, "children": []} for item in categories}
        roots = []
        for item in by_name.values():
            parent = item.get("parent")
            if parent and parent in by_name:
                by_name[parent]["children"].append(item)
            else:
                roots.append(item)
        return roots

    def bulk_import_categories(self, items: list[dict]) -> dict:
        created = [self.create_category(item) for item in items]
        return {"created": len(created), "items": created}

    def list_topics(self) -> list[dict]:
        topics = list(self.db.execute(select(ResourceTopic).order_by(ResourceTopic.created_at.desc())).scalars())
        return [self.topic_to_dict(topic) for topic in topics]

    def create_topic(self, payload: dict) -> dict:
        topic = ResourceTopic(title=payload["title"], description=payload.get("description", ""), accent=payload.get("accent"))
        self.db.add(topic)
        self.db.commit()
        self.db.refresh(topic)
        return self.topic_to_dict(topic)

    def add_video_to_topic(self, topic_id: int, video_id: int) -> dict:
        video = self.db.get(ResourceVideo, video_id)
        if video is None:
            raise ResourceInputError(f"Video {video_id} was not found.")

        existing = self.db.execute(
            select(ResourceTopicVideo).where(ResourceTopicVideo.topic_id == topic_id, ResourceTopicVideo.video_id == video_id)
        ).scalar_one_or_none()
        if existing is None:
            self.db.add(ResourceTopicVideo(topic_id=topic_id, video_id=video_id))
            self.db.commit()
        return {"topicId": topic_id, "videoId": video_id, "added": True, "video": self.video_to_dict(video)}

    def remove_video_from_topic(self, topic_id: int, video_id: int) -> dict:
        self.db.execute(delete(ResourceTopicVideo).where(ResourceTopicVideo.topic_id == topic_id, ResourceTopicVideo.video_id == video_id))
        self.db.commit()
        return {"topicId": topic_id, "videoId": video_id, "removed": True}

    def topic_videos(self, topic_id: int) -> dict:
        ids = [row.video_id for row in self.db.execute(select(ResourceTopicVideo).where(ResourceTopicVideo.topic_id == topic_id)).scalars()]
        if not ids:
            return {"items": [], "total": 0}
        videos = list(self.db.execute(select(ResourceVideo).where(ResourceVideo.id.in_(ids))).scalars())
        return {"items": [self.video_to_dict(video) for video in videos], "total": len(videos)}

    def list_notifications(self) -> list[dict]:
        rows = self.db.execute(select(ResourceNotification).order_by(ResourceNotification.time.desc())).scalars()
        return [self.notification_to_dict(row) for row in rows]

    def create_notification(self, payload: dict) -> dict:
        notification = ResourceNotification(title=payload["title"], message=payload.get("message", ""))
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        return self.notification_to_dict(notification)

    def mark_notification_read(self, notification_id: int) -> dict | None:
        notification = self.db.get(ResourceNotification, notification_id)
        if not notification:
            return None
        notification.read = True
        self.db.commit()
        self.db.refresh(notification)
        return self.notification_to_dict(notification)

    def mark_all_notifications_read(self) -> dict:
        notifications = list(self.db.execute(select(ResourceNotification).where(ResourceNotification.read == False)).scalars())  # noqa: E712
        for item in notifications:
            item.read = True
        self.db.commit()
        return {"updated": len(notifications)}

    def video_to_dict(self, video: ResourceVideo) -> dict:
        video_task = self._latest_video_task(video)
        video_info = self._video_task_info(video_task)
        return {
            "id": video.id,
            "title": video.title,
            "source": video.source,
            "sourceUrl": video.source_url,
            "finalUrl": video_info.get("finalUrl") if video_info else video.source_url,
            "platform": video_info.get("platform") if video_info else self._platform_from_source(video.source),
            "category": video.category,
            "tags": json.loads(video.tags or "[]"),
            "description": video.description,
            "cover": video.cover or (video_info.get("thumbnailUrl") if video_info else ""),
            "thumbnailUrl": (video_info.get("thumbnailUrl") if video_info else None) or video.cover,
            "duration": video.duration or (video_info.get("duration") if video_info else ""),
            "views": video.views or (video_info.get("viewCount") if video_info else "0"),
            "directVideoUrl": video_info.get("directVideoUrl") if video_info else None,
            "downloadRequested": video_info.get("downloadRequested") if video_info else False,
            "downloadStatus": video_info.get("downloadStatus") if video_info else "not_requested",
            "downloadUrl": video_info.get("downloadUrl") if video_info else None,
            "playUrl": self._play_url(video, video_info),
            "videoTaskId": video_info.get("taskId") if video_info else None,
            "videoInfo": video_info,
            "favorite": video.favorite,
            "createdAt": video.created_at.isoformat(),
            "notes": video.notes,
        }

    def _with_video_task_defaults(self, payload: dict) -> dict:
        task_id = payload.get("videoTaskId") or payload.get("video_task_id")
        if not task_id:
            return payload

        try:
            task = self.db.get(VideoTask, int(task_id))
        except (TypeError, ValueError) as exc:
            raise ResourceInputError("videoTaskId must be a number.") from exc

        if task is None:
            raise ResourceInputError(f"Video task {task_id} was not found.")

        enriched = dict(payload)
        enriched.setdefault("title", task.title or task.url)
        enriched.setdefault("source", self._source_from_platform(task.platform))
        enriched.setdefault("sourceUrl", task.url)
        enriched.setdefault("description", task.description or "")
        enriched.setdefault("cover", task.thumbnail_url or "")
        enriched.setdefault("duration", task.duration or "")
        enriched.setdefault("views", task.view_count or 0)
        return enriched

    def _latest_video_task(self, video: ResourceVideo) -> VideoTask | None:
        stmt = (
            select(VideoTask)
            .where((VideoTask.url == video.source_url) | (VideoTask.final_url == video.source_url))
            .order_by(VideoTask.created_at.desc(), VideoTask.id.desc())
            .limit(1)
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def _video_task_info(self, task: VideoTask | None) -> dict | None:
        if task is None:
            return None

        payload = VideoService(self.db)._to_dict(task)
        return {
            "taskId": payload["id"],
            "url": payload["url"],
            "finalUrl": payload["final_url"],
            "platform": payload["platform"],
            "title": payload["title"],
            "author": payload["author"],
            "description": payload["description"],
            "thumbnailUrl": payload["thumbnail_url"],
            "duration": payload["duration"],
            "publishedAt": payload["published_at"],
            "viewCount": payload["view_count"],
            "directVideoUrl": payload["direct_video_url"],
            "downloadRequested": payload["download_requested"],
            "downloadStatus": payload["download_status"],
            "downloadUrl": payload["download_url"],
            "storagePath": payload["download_path"],
            "status": payload["status"],
            "errorMessage": payload["error_message"],
        }

    def _play_url(self, video: ResourceVideo, video_info: dict | None) -> str:
        if video_info:
            return video_info.get("downloadUrl") or video_info.get("directVideoUrl") or video_info.get("finalUrl") or video.source_url
        return video.source_url

    def _source_from_platform(self, platform: str | None) -> str:
        mapping = {
            "bilibili": "Bilibili",
            "youtube": "YouTube",
            "direct_video": "项目组",
        }
        return mapping.get((platform or "").lower(), "项目组")

    def _platform_from_source(self, source: str) -> str:
        mapping = {
            "Bilibili": "bilibili",
            "YouTube": "youtube",
            "官网": "official",
            "高校公开课": "course",
            "项目组": "project",
        }
        return mapping.get(source, source.lower())

    def category_to_dict(self, category: ResourceCategory) -> dict:
        return {
            "id": category.id,
            "name": category.name,
            "parent": category.parent,
            "icon": category.icon,
            "order": category.order,
            "status": category.status,
            "description": category.description,
            "updatedAt": category.updated_at.isoformat(),
        }

    def topic_to_dict(self, topic: ResourceTopic) -> dict:
        count = self.db.execute(select(ResourceTopicVideo).where(ResourceTopicVideo.topic_id == topic.id)).scalars().all()
        return {
            "id": topic.id,
            "title": topic.title,
            "description": topic.description,
            "count": len(count),
            "accent": topic.accent,
        }

    def notification_to_dict(self, notification: ResourceNotification) -> dict:
        return {
            "id": notification.id,
            "title": notification.title,
            "message": notification.message,
            "time": notification.time.isoformat(),
            "read": notification.read,
        }

    def _views_number(self, value: str) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0
