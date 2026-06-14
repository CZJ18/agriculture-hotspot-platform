from fastapi import Header, HTTPException, status

from app.config import get_settings


def require_bearer_token(authorization: str | None = Header(default=None)) -> None:
    expected = f"Bearer {get_settings().mcp_bearer_token}"
    if authorization != expected:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid bearer token.")
