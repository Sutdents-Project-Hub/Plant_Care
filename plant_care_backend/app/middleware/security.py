from __future__ import annotations

from collections import defaultdict, deque
from threading import Lock
from time import monotonic

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


class PublicRateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        *,
        requests: int,
        window_seconds: int,
        protected_paths: list[str],
    ) -> None:
        super().__init__(app)
        self.requests = requests
        self.window_seconds = window_seconds
        self.protected_paths = tuple(protected_paths)
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._lock = Lock()

    async def dispatch(self, request: Request, call_next):
        if not self._should_limit(request):
            return await call_next(request)

        key = self._bucket_key(request)
        now = monotonic()
        retry_after = 0

        with self._lock:
            bucket = self._hits[key]
            cutoff = now - self.window_seconds
            while bucket and bucket[0] <= cutoff:
                bucket.popleft()

            if len(bucket) >= self.requests:
                retry_after = max(1, int(self.window_seconds - (now - bucket[0])))
            else:
                bucket.append(now)

        if retry_after > 0:
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests"},
                headers={"Retry-After": str(retry_after)},
            )

        return await call_next(request)

    def _should_limit(self, request: Request) -> bool:
        path = request.url.path
        if path == "/health":
            return False
        return any(path == protected or path.startswith(f"{protected}/") for protected in self.protected_paths)

    def _bucket_key(self, request: Request) -> str:
        forwarded_for = request.headers.get("x-forwarded-for", "")
        client_ip = forwarded_for.split(",")[0].strip()
        if not client_ip and request.client is not None:
            client_ip = request.client.host
        if not client_ip:
            client_ip = "unknown"
        return f"{client_ip}:{request.url.path}"
