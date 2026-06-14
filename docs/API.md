# API

Base URL: `http://localhost:8000/api`

## Hotspots

- `GET /hotspots?platform=&limit=100`
- `GET /hotspots/platforms`

## Crawlers

- `POST /crawler/run`
- `POST /crawler/run/{platform}`
- `POST /crawler/request`
- `GET /crawler/requests`
- `GET /crawler/requests/{request_id}`

Platforms: `github_trending`, `hacker_news`, `news_rss`, `bilibili`, `zhihu`, `weibo`, `douyin`, `wechat_channels`, `youtube`.

If a platform requires login or browser verification, `POST /crawler/run/{platform}` returns HTTP `428`:

```json
{
  "detail": {
    "status": "auth_required",
    "platform": "zhihu",
    "login_url": "https://www.zhihu.com/signin",
    "cookie_env": "ZHIHU_COOKIE",
    "message": "Login or browser verification is required."
  }
}
```

The frontend should show a modal with the login URL and tell the user to update the named `.env` cookie value.

YouTube uses the official YouTube Data API and requires `YOUTUBE_API_KEY`.
WeChat Channels has no stable public anonymous hot-list API; configure `HOTSPOT_FALLBACK_BASE_URL` or handle login/manual data export.

Frontend request flow:

```http
POST /crawler/request
Content-Type: application/json
```

```json
{
  "platform": "bilibili",
  "includeHotspots": true,
  "limit": 50
}
```

The API returns immediately:

```json
{
  "status": "accepted",
  "requestId": 12,
  "platform": "bilibili"
}
```

Then poll:

```http
GET /crawler/requests/12
```

Possible statuses: `pending`, `running`, `completed`, `auth_required`, `error`.

## Analysis

- `POST /analysis/daily`
- `GET /analysis/latest`

Request:

```json
{ "date": "2026-06-14" }
```

## Custom URL

- `POST /custom-url/submit`
- `GET /custom-url/tasks`
- `GET /custom-url/tasks/{task_id}`
- `POST /custom-url/analyze`

Request:

```json
{ "url": "https://example.com/news/xxx" }
```

## Export

- `GET /export/hotspots.xlsx?platform=github_trending`

## Video URLs

- `POST /video/parse`
- `GET /video/tasks`
- `GET /video/tasks/{task_id}`
- `GET /video/files/{filename}`

Request:

```json
{
  "url": "https://www.youtube.com/watch?v=xxx",
  "download": false
}
```

`download=true` only downloads public direct video files discovered in page metadata or direct `.mp4/.webm/.mov` links. The backend does not bypass login, CAPTCHA, DRM, paywalls, signed platform streams, or platform extraction protections.

If `VIDEO_YTDLP_ENABLED=true`, non-direct supported platform URLs can be delegated to `yt-dlp` under the configured domain allowlist and file-size limit.

## Agricultural Video Resources

Base prefix: `/api/resources`

Videos:

- `GET /resources/videos`
- `POST /resources/videos`
- `PUT /resources/videos/{video_id}`
- `DELETE /resources/videos/{video_id}`
- `POST /resources/videos/{video_id}/favorite`
- `PATCH /resources/videos/{video_id}/notes`

Video query parameters:

- `keyword`
- `category`
- `source`
- `topicId`
- `favorite`
- `sort=latest|hot|favorite`

Categories:

- `GET /resources/categories`
- `POST /resources/categories`
- `PUT /resources/categories/{category_id}`
- `DELETE /resources/categories/{category_id}`
- `GET /resources/categories/tree`
- `PATCH /resources/categories/{category_id}/status`
- `POST /resources/categories/bulk-import`
- `GET /resources/categories/export`

Topics:

- `GET /resources/topics`
- `POST /resources/topics`
- `GET /resources/topics/{topic_id}/videos`
- `POST /resources/topics/{topic_id}/videos`
- `DELETE /resources/topics/{topic_id}/videos/{video_id}`

Notifications:

- `GET /resources/notifications`
- `POST /resources/notifications`
- `PATCH /resources/notifications/{notification_id}/read`
- `POST /resources/notifications/read-all`
