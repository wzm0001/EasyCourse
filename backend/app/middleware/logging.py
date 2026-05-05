import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from app.models.log import LogType, LogLevel


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        method = request.method.upper()
        if method not in ("POST", "PUT", "DELETE"):
            return await call_next(request)

        start_time = time.time()
        response = await call_next(request)
        duration = time.time() - start_time

        try:
            from app.database import AsyncSessionLocal
            from app.services.log import log_operation

            user_id = None
            username = ""
            school_id = None

            auth_header = request.headers.get("authorization", "")
            if auth_header and auth_header.startswith("Bearer "):
                try:
                    from app.services.auth import get_current_user
                    token = auth_header.split(" ")[1]
                    async with AsyncSessionLocal() as db:
                        user = await get_current_user(token, db)
                        if user:
                            user_id = user.id
                            username = user.username
                            school_id = user.school_id
                except Exception:
                    pass

            path = request.url.path
            action = f"{method} {path}"
            detail = f"状态码: {response.status_code}, 耗时: {duration:.3f}s"
            ip_address = request.client.host if request.client else ""

            async with AsyncSessionLocal() as db:
                try:
                    await log_operation(
                        user_id=user_id,
                        username=username,
                        school_id=school_id,
                        action=action,
                        target_type="api",
                        target_id="",
                        detail=detail,
                        ip_address=ip_address,
                        db=db,
                    )
                    await db.commit()
                except Exception:
                    await db.rollback()
        except Exception:
            pass

        return response
