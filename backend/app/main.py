from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db, close_db
from app.routers import health
from app.routers import auth
from app.routers import schools
from app.routers import users
from app.routers import approvals
from app.routers import semesters
from app.routers import periods
from app.routers import basic_data
from app.routers import constraints
from app.routers import schedules
from app.routers import teaching_classes
from app.routers import exports
from app.routers import logs
from app.routers import notifications
from app.routers import backups
from app.routers import settings as settings_router
from app.middleware.logging import LoggingMiddleware
from app.middleware.security import CSRFMiddleware, RateLimitMiddleware
from app.middleware.maintenance import MaintenanceMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    from app.services.backup import setup_auto_backup
    scheduler = setup_auto_backup(None)
    yield
    scheduler.shutdown()
    await close_db()


app = FastAPI(
    title="走班排课系统",
    description="中小学走班排课系统后端API",
    version="1.0.0",
    lifespan=lifespan,
    debug=settings.DEBUG,
)

app.add_middleware(MaintenanceMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(CSRFMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
app.include_router(schools.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(approvals.router, prefix="/api/v1")
app.include_router(semesters.router, prefix="/api/v1")
app.include_router(periods.router, prefix="/api/v1")
app.include_router(basic_data.router, prefix="/api/v1")
app.include_router(constraints.router, prefix="/api/v1")
app.include_router(schedules.router, prefix="/api/v1")
app.include_router(teaching_classes.router, prefix="/api/v1")
app.include_router(exports.router, prefix="/api/v1")
app.include_router(logs.router, prefix="/api/v1")
app.include_router(notifications.router, prefix="/api/v1")
app.include_router(backups.router, prefix="/api/v1")
app.include_router(settings_router.router, prefix="/api/v1")
app.include_router(settings_router.security_router, prefix="/api/v1")
