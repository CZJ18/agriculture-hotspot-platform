# Render Deployment

This project can deploy the FastAPI backend to Render with `render.yaml`.

## What Render Creates

- Web service: `agriculture-hotspot-api`
- PostgreSQL database: `agriculture-hotspot-db`
- Health check: `/health`
- API docs: `/docs`
- OpenAPI schema: `/openapi.json`
- API prefix: `/api`

## Prepare Git

Render Blueprint deployments must read this repository from GitHub, GitLab, or Bitbucket.

```bash
git remote -v
git add render.yaml runtime.txt backend/requirements.txt backend/app/config.py backend/app/database.py docs/RENDER.md
git commit -m "Add Render deployment configuration"
git push origin main
```

If `git remote -v` is empty, create a remote repository first, then add it:

```bash
git remote add origin https://github.com/<user>/<repo>.git
git branch -M main
git push -u origin main
```

## Deploy

Open Render's Blueprint page and select the pushed repository:

```text
https://dashboard.render.com/blueprint/new
```

Render will detect `render.yaml`, create the web service and database, and inject `DATABASE_URL` automatically.

## Required Settings After Deploy

Set `CORS_ORIGINS` to include the frontend domain after the frontend is deployed:

```env
CORS_ORIGINS=http://127.0.0.1:5173,http://localhost:5173,https://your-frontend.vercel.app
```

Platform credentials are optional, but needed when a crawler returns `auth_required`:

```env
BILIBILI_COOKIE=
ZHIHU_COOKIE=
WEIBO_COOKIE=
DOUYIN_COOKIE=
WECHAT_CHANNELS_COOKIE=
YOUTUBE_API_KEY=
```

## Public URLs

After deployment, Render provides a URL like:

```text
https://agriculture-hotspot-api.onrender.com
```

Use these checks:

```text
https://agriculture-hotspot-api.onrender.com/health
https://agriculture-hotspot-api.onrender.com/docs
https://agriculture-hotspot-api.onrender.com/openapi.json
```

The frontend API base URL should be:

```text
https://agriculture-hotspot-api.onrender.com/api
```

## Notes

- `VIDEO_DOWNLOAD_ENABLED` and `VIDEO_YTDLP_ENABLED` are disabled by default on Render.
- Render free web services can sleep after inactivity, so the first request may be slow.
- Render free PostgreSQL databases expire after 30 days and do not include backups. Upgrade the database before using it for long-term data.
- The in-process scheduler is not a reliable production cron on free sleeping services. Use Render Cron Jobs later for stable scheduled crawling.
- `PUBLIC_API_AUTH_ENABLED` is set to `false` for easier frontend integration. Turn it on before exposing crawler or download endpoints publicly.
