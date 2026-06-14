import uvicorn

from app.config import get_settings


if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.public_api_host,
        port=settings.public_api_port,
        reload=False,
    )
