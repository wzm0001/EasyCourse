import csv
import io
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.schemas.common import APIResponse, PageResponse
from app.schemas.log import LogQuery, LogInfo
from app.services.log import query_logs
from app.middleware.auth import require_super_admin

router = APIRouter(prefix="/logs", tags=["日志管理"])


@router.get("", response_model=APIResponse[PageResponse[LogInfo]])
async def get_logs(
    log_type: str = None,
    level: str = None,
    user_id: str = None,
    start_date: str = None,
    end_date: str = None,
    keyword: str = None,
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db),
):
    from datetime import datetime
    from app.models.log import LogType as LT, LogLevel as LL

    query = LogQuery(page=page, page_size=page_size)
    if log_type:
        try:
            query.log_type = LT(log_type)
        except ValueError:
            pass
    if level:
        try:
            query.level = LL(level)
        except ValueError:
            pass
    if user_id:
        query.user_id = user_id
    if start_date:
        try:
            query.start_date = datetime.fromisoformat(start_date)
        except ValueError:
            pass
    if end_date:
        try:
            query.end_date = datetime.fromisoformat(end_date)
        except ValueError:
            pass
    if keyword:
        query.keyword = keyword

    result = await query_logs(query, db)
    return APIResponse.success(data=result)


@router.get("/export", response_model=None)
async def export_logs(
    log_type: str = None,
    level: str = None,
    user_id: str = None,
    start_date: str = None,
    end_date: str = None,
    keyword: str = None,
    current_user: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db),
):
    from datetime import datetime
    from app.models.log import LogType as LT, LogLevel as LL

    query = LogQuery(page=1, page_size=10000)
    if log_type:
        try:
            query.log_type = LT(log_type)
        except ValueError:
            pass
    if level:
        try:
            query.level = LL(level)
        except ValueError:
            pass
    if user_id:
        query.user_id = user_id
    if start_date:
        try:
            query.start_date = datetime.fromisoformat(start_date)
        except ValueError:
            pass
    if end_date:
        try:
            query.end_date = datetime.fromisoformat(end_date)
        except ValueError:
            pass
    if keyword:
        query.keyword = keyword

    result = await query_logs(query, db)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "日志类型", "级别", "用户ID", "用户名", "学校ID", "操作", "目标类型", "目标ID", "详情", "IP地址", "创建时间"])
    for item in result.items:
        writer.writerow([
            item.id, item.log_type.value, item.level.value, item.user_id or "",
            item.username, item.school_id or "", item.action, item.target_type,
            item.target_id, item.detail, item.ip_address, item.created_at.isoformat(),
        ])

    content = output.getvalue()
    output.close()
    return Response(
        content=content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=logs_export.csv"},
    )
