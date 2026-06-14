from collections import defaultdict, deque
from time import monotonic

from fastapi import HTTPException, Request, status

from app.config import get_settings


class InMemoryRateLimiter:
    def __init__(self, limit: int, window_seconds: int = 60) -> None:
        self.limit = limit
        self.window_seconds = window_seconds
        self._hits: dict[str, deque[float]] = defaultdict(deque)

    def check(self, key: str) -> None:
        now = monotonic()
        hits = self._hits[key]
        while hits and now - hits[0] > self.window_seconds:
            hits.popleft()
        if len(hits) >= self.limit:
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Rate limit exceeded.")
        hits.append(now)


limiter = InMemoryRateLimiter(get_settings().rate_limit_per_minute)


def enforce_rate_limit(request: Request) -> None:
    client = request.client.host if request.client else "anonymous"
    limiter.check(client)
