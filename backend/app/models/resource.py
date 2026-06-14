from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ResourceVideo(Base):
    __tablename__ = "resource_videos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(500), index=True)
    source: Mapped[str] = mapped_column(String(80), index=True)
    source_url: Mapped[str] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(120), index=True)
    tags: Mapped[str] = mapped_column(Text, default="[]")
    description: Mapped[str] = mapped_column(Text, default="")
    cover: Mapped[str] = mapped_column(Text, default="")
    duration: Mapped[str] = mapped_column(String(80), default="")
    views: Mapped[str] = mapped_column(String(80), default="0", index=True)
    favorite: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ResourceCategory(Base):
    __tablename__ = "resource_categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), index=True)
    parent: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    icon: Mapped[str] = mapped_column(String(120), default="")
    order: Mapped[int] = mapped_column(Integer, default=0, index=True)
    status: Mapped[str] = mapped_column(String(40), default="启用", index=True)
    description: Mapped[str] = mapped_column(Text, default="")
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ResourceTopic(Base):
    __tablename__ = "resource_topics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), index=True)
    description: Mapped[str] = mapped_column(Text, default="")
    accent: Mapped[str | None] = mapped_column(String(40), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ResourceTopicVideo(Base):
    __tablename__ = "resource_topic_videos"
    __table_args__ = (UniqueConstraint("topic_id", "video_id", name="uq_resource_topic_video"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    topic_id: Mapped[int] = mapped_column(Integer, index=True)
    video_id: Mapped[int] = mapped_column(Integer, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ResourceNotification(Base):
    __tablename__ = "resource_notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200))
    message: Mapped[str] = mapped_column(Text, default="")
    time: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    read: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
