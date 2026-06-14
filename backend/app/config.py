import os
from functools import lru_cache
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Hotspot AI System"
    api_prefix: str = "/api"
    public_api_host: str = "0.0.0.0"
    public_api_port: int = 8000
    public_api_auth_enabled: bool = False
    public_api_key: str = ""
    database_url: str = "sqlite:///./hotspot_ai.db"
    cors_origins: List[str] = Field(default_factory=lambda: ["http://127.0.0.1:5173", "http://localhost:5173"])

    ai_provider: str = "mock"
    ai_api_key: str = ""
    ai_base_url: str = ""
    ai_model: str = ""

    request_timeout_seconds: float = 10.0
    max_response_bytes: int = 2 * 1024 * 1024
    max_redirects: int = 3
    crawler_min_interval_seconds: float = 1.0
    rate_limit_per_minute: int = 30
    hotspot_fallback_base_url: str = ""
    bilibili_cookie: str = ""
    zhihu_cookie: str = ""
    weibo_cookie: str = ""
    douyin_cookie: str = ""
    wechat_channels_cookie: str = ""
    youtube_api_key: str = ""
    youtube_region_code: str = "US"
    video_download_enabled: bool = True
    video_download_dir: str = "./downloads/videos"
    video_max_download_bytes: int = 50 * 1024 * 1024
    video_ytdlp_enabled: bool = False
    video_ytdlp_allowed_domains: List[str] = Field(
        default_factory=lambda: [
            "youtube.com",
            "youtu.be",
            "bilibili.com",
            "b23.tv",
            "douyin.com",
            "iesdouyin.com",
            "weibo.com",
        ]
    )
    video_ytdlp_cookie_file: str = ""

    mcp_bearer_token: str = "change-me"
    allowed_origins: List[str] = Field(default_factory=lambda: ["http://localhost:5173"])

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @field_validator("cors_origins", "allowed_origins", "video_ytdlp_allowed_domains", mode="before")
    @classmethod
    def split_csv(cls, value):
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    render_port = os.getenv("PORT")
    if render_port:
        settings.public_api_port = int(render_port)
    return settings
