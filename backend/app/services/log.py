from typing import Optional
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.log import SystemLog, LogType, LogLevel
from app.repositories.log import SystemLogRepository
from app.schemas.log import LogQuery, LogInfo
from app.schemas.common import PageResponse


async def log_operation(
    user_id: str,
    username: str,
    school_id: Optional[str],
    action: str,
    target_type: str,
    target_id: str,
    detail: str,
    ip_address: str,
    db: AsyncSession,
) -> SystemLog:
    repo = SystemLogRepository(db)
    log = SystemLog(
        log_type=LogType.OPERATION,
        level=LogLevel.INFO,
        user_id=user_id,
        username=username,
        school_id=school_id,
        action=action,
        target_type=target_type,
        target_id=target_id,
        detail=detail,
        ip_address=ip_address,
    )
    log = await repo.create(log)
    return log


async def log_login(
    user_id: str,
    username: str,
    school_id: Optional[str],
    ip_address: str,
    success: bool,
    db: AsyncSession,
) -> SystemLog:
    repo = SystemLogRepository(db)
    log = SystemLog(
        log_type=LogType.LOGIN,
        level=LogLevel.INFO if success else LogLevel.WARNING,
        user_id=user_id if success else None,
        username=username,
        school_id=school_id if success else None,
        action="登录成功" if success else "登录失败",
        detail="" if success else f"用户 {username} 登录失败",
        ip_address=ip_address,
    )
    log = await repo.create(log)
    return log


async def log_system(
    level: LogLevel,
    action: str,
    detail: str,
    stack_trace: str,
    db: AsyncSession,
) -> SystemLog:
    repo = SystemLogRepository(db)
    log = SystemLog(
        log_type=LogType.SYSTEM,
        level=level,
        action=action,
        detail=detail,
        stack_trace=stack_trace,
    )
    log = await repo.create(log)
    return log


async def log_schedule(
    user_id: str,
    username: str,
    school_id: Optional[str],
    action: str,
    detail: str,
    db: AsyncSession,
) -> SystemLog:
    repo = SystemLogRepository(db)
    log = SystemLog(
        log_type=LogType.SCHEDULE,
        level=LogLevel.INFO,
        user_id=user_id,
        username=username,
        school_id=school_id,
        action=action,
        detail=detail,
    )
    log = await repo.create(log)
    return log


async def query_logs(query: LogQuery, db: AsyncSession) -> PageResponse[LogInfo]:
    conditions = []
    if query.log_type:
        conditions.append(SystemLog.log_type == query.log_type)
    if query.level:
        conditions.append(SystemLog.level == query.level)
    if query.user_id:
        conditions.append(SystemLog.user_id == query.user_id)
    if query.start_date:
        conditions.append(SystemLog.created_at >= query.start_date)
    if query.end_date:
        conditions.append(SystemLog.created_at <= query.end_date)
    if query.keyword:
        pattern = f"%{query.keyword}%"
        conditions.append(
            (SystemLog.action.ilike(pattern)) | (SystemLog.detail.ilike(pattern)) | (SystemLog.username.ilike(pattern))
        )

    where_clause = and_(*conditions) if conditions else True

    count_result = await db.execute(
        select(func.count()).select_from(SystemLog).where(where_clause)
    )
    total = count_result.scalar_one()

    offset = (query.page - 1) * query.page_size
    result = await db.execute(
        select(SystemLog).where(where_clause).order_by(SystemLog.created_at.desc()).offset(offset).limit(query.page_size)
    )
    items = [LogInfo.model_validate(log) for log in result.scalars().all()]

    return PageResponse(items=items, total=total, page=query.page, page_size=query.page_size)
