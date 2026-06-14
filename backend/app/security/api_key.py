from fastapi import Request


PUBLIC_EXEMPT_PATHS = {"/health", "/docs", "/redoc", "/openapi.json"}


def is_public_path(path: str) -> bool:
    return path in PUBLIC_EXEMPT_PATHS or path.startswith("/docs/")


def is_valid_api_key(request: Request, expected_key: str) -> bool:
    if not expected_key:
        return False
    header_key = request.headers.get("x-api-key")
    bearer = request.headers.get("authorization", "")
    return header_key == expected_key or bearer == f"Bearer {expected_key}"
