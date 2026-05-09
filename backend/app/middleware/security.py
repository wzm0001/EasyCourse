import os
import re
import time
import secrets
from collections import defaultdict
from typing import Dict, Tuple, Optional, Any

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from app.config import settings


_csrf_tokens: Dict[str, float] = {}
CSRF_TOKEN_EXPIRE = 480 * 60

_rate_limits: Dict[str, Dict[str, Tuple[int, float]]] = {}
RATE_LIMIT_CLEANUP_INTERVAL = 60
_last_cleanup = time.time()

CONFLICT_CHECK_RATE_LIMIT = 300
DEFAULT_RATE_LIMIT = 60
LOGIN_RATE_LIMIT = 5
RATE_WINDOW = 60


def _cleanup_rate_limits():
    global _last_cleanup
    now = time.time()
    if now - _last_cleanup < RATE_LIMIT_CLEANUP_INTERVAL:
        return
    _last_cleanup = now
    expired_ips = []
    for ip, endpoints in _rate_limits.items():
        expired_endpoints = []
        for endpoint, (count, window_start) in endpoints.items():
            if now - window_start > RATE_WINDOW * 2:
                expired_endpoints.append(endpoint)
        for endpoint in expired_endpoints:
            del endpoints[endpoint]
        if not endpoints:
            expired_ips.append(ip)
    for ip in expired_ips:
        del _rate_limits[ip]


def _cleanup_csrf_tokens():
    now = time.time()
    expired = [token for token, exp in _csrf_tokens.items() if now > exp]
    for token in expired:
        del _csrf_tokens[token]


def generate_csrf_token() -> str:
    _cleanup_csrf_tokens()
    token = secrets.token_hex(32)
    _csrf_tokens[token] = time.time() + CSRF_TOKEN_EXPIRE
    return token


def validate_csrf_token(token: str) -> bool:
    if token not in _csrf_tokens:
        return False
    if time.time() > _csrf_tokens[token]:
        del _csrf_tokens[token]
        return False
    return True


def sanitize_string(s: str) -> str:
    if not isinstance(s, str):
        return s
    s = re.sub(r"<[^>]*>", "", s)
    s = re.sub(r"javascript:", "", s, flags=re.IGNORECASE)
    s = re.sub(r"on\w+\s*=", "", s, flags=re.IGNORECASE)
    return s.strip()


def validate_input(data: Any) -> Any:
    if isinstance(data, str):
        return sanitize_string(data)
    elif isinstance(data, dict):
        return {k: validate_input(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [validate_input(item) for item in data]
    return data


async def check_single_session(user_id: str, token: str, db) -> bool:
    from app.repositories.user import UserRepository
    repo = UserRepository(db)
    user = await repo.get_by_id(user_id)
    if user is None:
        return False
    if not hasattr(user, "current_token") or not user.current_token:
        return True
    return user.current_token == token


class CSRFMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        if settings.DEBUG:
            return await call_next(request)

        if request.method in ("GET", "HEAD", "OPTIONS"):
            return await call_next(request)

        if request.url.path == "/api/v1/security/csrf-token":
            return await call_next(request)

        csrf_token = request.headers.get("X-CSRF-Token")
        if not csrf_token or not validate_csrf_token(csrf_token):
            return JSONResponse(
                status_code=403,
                content={"detail": "CSRF token验证失败"},
            )

        return await call_next(request)


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        _cleanup_rate_limits()

        client_ip = request.client.host if request.client else "unknown"
        path = request.url.path

        if "/auth/login" in path:
            limit = LOGIN_RATE_LIMIT
        elif "/schedules/conflict-check" in path:
            limit = CONFLICT_CHECK_RATE_LIMIT
        else:
            limit = DEFAULT_RATE_LIMIT

        now = time.time()
        if client_ip not in _rate_limits:
            _rate_limits[client_ip] = {}

        if path not in _rate_limits[client_ip]:
            _rate_limits[client_ip][path] = (1, now)
        else:
            count, window_start = _rate_limits[client_ip][path]
            if now - window_start > RATE_WINDOW:
                _rate_limits[client_ip][path] = (1, now)
            else:
                count += 1
                _rate_limits[client_ip][path] = (count, window_start)
                if count > limit:
                    return JSONResponse(
                        status_code=429,
                        content={"detail": "请求过于频繁，请稍后再试"},
                    )

        return await call_next(request)
