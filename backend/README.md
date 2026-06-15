# Backend

FastAPI backend for the multi-platform hotspot aggregation and AI trend analysis system.

## Run

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

To open the API to other devices on the network:

```bash
python run_public_api.py
```

Then visit `http://<lan-ip>:8000/docs`. Set `PUBLIC_API_AUTH_ENABLED=true` and `PUBLIC_API_KEY=...` before exposing it beyond your own machine.

## Stable Crawlers

- `github_trending`
- `hacker_news`
- `news_rss`

Chinese platform crawlers use public anonymous endpoints/pages only. They intentionally do not bypass login, CAPTCHA, anti-bot controls, paywalls, signed APIs, or private APIs. If a platform returns visitor/security verification, configure `HOTSPOT_FALLBACK_BASE_URL` to a trusted self-hosted public hot-list API.

## Optional Account Cookies

For platforms that block anonymous traffic, log in with an authorized browser account and copy the site cookie into `.env`:

```env
BILIBILI_COOKIE=
ZHIHU_COOKIE=
WEIBO_COOKIE=
DOUYIN_COOKIE=
WECHAT_CHANNELS_COOKIE=
YOUTUBE_API_KEY=
YOUTUBE_REGION_CODE=US
```

Do not put account passwords in `.env` or source code. If a platform asks for CAPTCHA or security verification, complete it manually in the browser; this project does not bypass verification.

When a crawler needs login, the API returns HTTP `428` with `status: auth_required`, `login_url`, and `cookie_env`. The frontend can use this response to show a login prompt/modal.

YouTube is implemented through the official Data API `videos.list?chart=mostPopular`; set `YOUTUBE_API_KEY` first. WeChat Channels should use a trusted configured fallback source or manual logged-in export because there is no stable anonymous public hot-list endpoint.

## Optional Video Download

Video metadata parsing is always available through `/api/video/parse`. Direct public video file downloads are controlled by:

```env
VIDEO_DOWNLOAD_ENABLED=true
VIDEO_DOWNLOAD_DIR=./downloads/videos
VIDEO_MAX_DOWNLOAD_BYTES=52428800
```

`yt-dlp` support is optional and disabled by default:

```env
VIDEO_YTDLP_ENABLED=false
VIDEO_YTDLP_ALLOWED_DOMAINS=youtube.com,youtu.be,bilibili.com,b23.tv,douyin.com,iesdouyin.com,weibo.com
VIDEO_YTDLP_COOKIE_FILE=
```

Enable it only for content the user has permission to download. This project does not implement DRM, paywall, login, CAPTCHA, or anti-bot bypass.

## Optional Cloudflare R2 Storage

Render free instances use temporary local files, so downloaded videos should be uploaded to object storage for long-term access. Cloudflare R2 works through its S3-compatible API:

```env
OBJECT_STORAGE_ENABLED=true
OBJECT_STORAGE_BUCKET=agriculture-videos
OBJECT_STORAGE_ENDPOINT_URL=https://<ACCOUNT_ID>.r2.cloudflarestorage.com
OBJECT_STORAGE_ACCESS_KEY_ID=<R2_ACCESS_KEY_ID>
OBJECT_STORAGE_SECRET_ACCESS_KEY=<R2_SECRET_ACCESS_KEY>
OBJECT_STORAGE_REGION=auto
OBJECT_STORAGE_PREFIX=videos
OBJECT_STORAGE_DELETE_LOCAL_AFTER_UPLOAD=true
```

If the bucket is public or has a custom domain, set:

```env
OBJECT_STORAGE_PUBLIC_BASE_URL=https://cdn.example.com
```

If `OBJECT_STORAGE_PUBLIC_BASE_URL` is empty, the API returns a temporary signed download URL. Control its lifetime with:

```env
OBJECT_STORAGE_PRESIGN_SECONDS=3600
```
