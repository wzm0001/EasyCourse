from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response


class MaintenanceMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        try:
            from app.database import AsyncSessionLocal
            from app.services.settings import is_maintenance_mode

            async with AsyncSessionLocal() as db:
                maintenance = await is_maintenance_mode(db)
                if not maintenance:
                    return await call_next(request)
        except Exception:
            return await call_next(request)

        auth_header = request.headers.get("authorization", "")
        if auth_header and auth_header.startswith("Bearer "):
            try:
                from app.services.auth import get_current_user
                from app.database import AsyncSessionLocal
                from app.models.user import UserRole

                token = auth_header.split(" ")[1]
                async with AsyncSessionLocal() as db:
                    user = await get_current_user(token, db)
                    if user and user.role == UserRole.SUPER_ADMIN:
                        return await call_next(request)
            except Exception:
                pass

        return JSONResponse(
            status_code=503,
            content={"detail": "系统维护中，请稍后再试"},
        )
