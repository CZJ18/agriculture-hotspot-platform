from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import init_db
from app.routers import analysis, crawler, custom_url, export, hotspots, resources, video
from app.scheduler.jobs import build_scheduler
from app.security.api_key import is_public_path, is_valid_api_key


settings = get_settings()
scheduler = build_scheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    scheduler.start()
    yield
    scheduler.shutdown(wait=False)


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def public_api_key_guard(request, call_next):
    if (
        settings.public_api_auth_enabled
        and request.url.path.startswith(settings.api_prefix)
        and not is_public_path(request.url.path)
        and not is_valid_api_key(request, settings.public_api_key)
    ):
        return JSONResponse(
            status_code=401,
            content={"detail": "Invalid or missing API key. Use X-API-Key or Authorization: Bearer <key>."},
        )
    return await call_next(request)

app.include_router(hotspots.router, prefix=settings.api_prefix)
app.include_router(crawler.router, prefix=settings.api_prefix)
app.include_router(analysis.router, prefix=settings.api_prefix)
app.include_router(export.router, prefix=settings.api_prefix)
app.include_router(custom_url.router, prefix=settings.api_prefix)
app.include_router(video.router, prefix=settings.api_prefix)
app.include_router(resources.router, prefix=settings.api_prefix)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
