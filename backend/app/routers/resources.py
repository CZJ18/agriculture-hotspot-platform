from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.resource_service import ResourceService

router = APIRouter(prefix="/resources", tags=["resources"])


@router.get("/videos")
def list_videos(
    keyword: str | None = None,
    category: str | None = None,
    source: str | None = None,
    topicId: int | None = None,
    favorite: bool | None = None,
    sort: str = Query(default="latest", pattern="^(latest|hot|favorite)$"),
    db: Session = Depends(get_db),
) -> dict:
    return ResourceService(db).list_videos(keyword, category, source, topicId, favorite, sort)


@router.post("/videos")
def create_video(payload: dict, db: Session = Depends(get_db)) -> dict:
    return ResourceService(db).create_video(payload)


@router.put("/videos/{video_id}")
def update_video(video_id: int, payload: dict, db: Session = Depends(get_db)) -> dict:
    video = ResourceService(db).update_video(video_id, payload)
    if video is None:
        raise HTTPException(status_code=404, detail="Video not found.")
    return video


@router.delete("/videos/{video_id}")
def delete_video(video_id: int, db: Session = Depends(get_db)) -> dict:
    return {"deleted": ResourceService(db).delete_video(video_id)}


@router.post("/videos/{video_id}/favorite")
def set_video_favorite(video_id: int, payload: dict, db: Session = Depends(get_db)) -> dict:
    video = ResourceService(db).set_favorite(video_id, bool(payload.get("favorite", True)))
    if video is None:
        raise HTTPException(status_code=404, detail="Video not found.")
    return video


@router.patch("/videos/{video_id}/notes")
def save_video_notes(video_id: int, payload: dict, db: Session = Depends(get_db)) -> dict:
    video = ResourceService(db).save_notes(video_id, str(payload.get("notes", "")))
    if video is None:
        raise HTTPException(status_code=404, detail="Video not found.")
    return video


@router.get("/categories")
def list_categories(db: Session = Depends(get_db)) -> list[dict]:
    return ResourceService(db).list_categories()


@router.post("/categories")
def create_category(payload: dict, db: Session = Depends(get_db)) -> dict:
    return ResourceService(db).create_category(payload)


@router.put("/categories/{category_id}")
def update_category(category_id: int, payload: dict, db: Session = Depends(get_db)) -> dict:
    category = ResourceService(db).update_category(category_id, payload)
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found.")
    return category


@router.delete("/categories/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_db)) -> dict:
    return {"deleted": ResourceService(db).delete_category(category_id)}


@router.get("/categories/tree")
def category_tree(db: Session = Depends(get_db)) -> list[dict]:
    return ResourceService(db).category_tree()


@router.patch("/categories/{category_id}/status")
def set_category_status(category_id: int, payload: dict, db: Session = Depends(get_db)) -> dict:
    category = ResourceService(db).update_category(category_id, {"status": payload.get("status", "启用")})
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found.")
    return category


@router.post("/categories/bulk-import")
def bulk_import_categories(payload: dict, db: Session = Depends(get_db)) -> dict:
    return ResourceService(db).bulk_import_categories(payload.get("items", []))


@router.get("/categories/export")
def export_categories(db: Session = Depends(get_db)) -> dict:
    items = ResourceService(db).list_categories()
    return {"items": items, "total": len(items)}


@router.get("/topics")
def list_topics(db: Session = Depends(get_db)) -> list[dict]:
    return ResourceService(db).list_topics()


@router.post("/topics")
def create_topic(payload: dict, db: Session = Depends(get_db)) -> dict:
    return ResourceService(db).create_topic(payload)


@router.get("/topics/{topic_id}/videos")
def topic_videos(topic_id: int, db: Session = Depends(get_db)) -> dict:
    return ResourceService(db).topic_videos(topic_id)


@router.post("/topics/{topic_id}/videos")
def add_video_to_topic(topic_id: int, payload: dict, db: Session = Depends(get_db)) -> dict:
    return ResourceService(db).add_video_to_topic(topic_id, int(payload["videoId"]))


@router.delete("/topics/{topic_id}/videos/{video_id}")
def remove_video_from_topic(topic_id: int, video_id: int, db: Session = Depends(get_db)) -> dict:
    return ResourceService(db).remove_video_from_topic(topic_id, video_id)


@router.get("/notifications")
def list_notifications(db: Session = Depends(get_db)) -> list[dict]:
    return ResourceService(db).list_notifications()


@router.post("/notifications")
def create_notification(payload: dict, db: Session = Depends(get_db)) -> dict:
    return ResourceService(db).create_notification(payload)


@router.patch("/notifications/{notification_id}/read")
def mark_notification_read(notification_id: int, db: Session = Depends(get_db)) -> dict:
    notification = ResourceService(db).mark_notification_read(notification_id)
    if notification is None:
        raise HTTPException(status_code=404, detail="Notification not found.")
    return notification


@router.post("/notifications/read-all")
def mark_all_notifications_read(db: Session = Depends(get_db)) -> dict:
    return ResourceService(db).mark_all_notifications_read()
