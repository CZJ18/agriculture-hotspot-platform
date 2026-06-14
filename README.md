# Multi-platform Hotspot Aggregation and AI Trend Analysis System

This repository contains the backend-first implementation of the project described in the DOCX requirement.

Implemented now:

- FastAPI backend.
- SQLAlchemy models for `hotspots`, `daily_analysis`, and `custom_url_tasks`.
- Crawlers for GitHub Trending, Hacker News, RSS, Bilibili, Zhihu, Weibo, and Douyin.
- Custom URL security validation and public-page extraction.
- AI analysis abstraction with local fallback.
- Excel export.
- APScheduler jobs.
- MCP Streamable HTTP server.
- Frontend API client contract only.

Frontend pages and visual UI are intentionally deferred.

For Zhihu, Weibo, Douyin, Bilibili, WeChat Channels, and YouTube account/API-backed access, fill the corresponding `*_COOKIE` or `YOUTUBE_API_KEY` values in `backend/.env`. Password-based login is intentionally not implemented.

When login is needed, crawler APIs return `428 auth_required` with a login URL so the future frontend can open a modal instead of showing a generic failure.

Video links have a dedicated `/api/video/parse` endpoint. Users can request metadata only or set `download=true`; downloads are restricted to public direct video files by default.

Optional `yt-dlp` support can be enabled with `VIDEO_YTDLP_ENABLED=true`; MCP tools `parse_video_url`, `download_video_url`, and `get_video_task` call the same FastAPI video endpoints.

To let other devices call the backend API, run `backend/run_public_api.py` and open `http://<lan-ip>:8000/docs`. Optional API key protection is documented in `docs/PUBLIC_API.md`.

## Render Deployment

The backend can be deployed to Render with the Blueprint in `render.yaml`. See `docs/RENDER.md` for the deployment checklist, required environment variables, and post-deploy URLs.
