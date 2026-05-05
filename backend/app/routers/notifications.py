from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User, UserRole
from app.schemas.common import APIResponse, PageResponse
from app.schemas.notification import NotificationCreate, NotificationBatchCreate, NotificationInfo
from app.services.notification import (
    get_notifications, get_unread_count, mark_as_read, mark_all_as_read,
    create_notification, create_batch_notifications,
)
from app.middleware.auth import get_current_user_dependency, require_super_admin, require_role

router = APIRouter(prefix="/notifications", tags=["通知管理"])


@router.get("", response_model=APIResponse[PageResponse[NotificationInfo]])
async def list_notifications(
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    result = await get_notifications(current_user.id, page, page_size, db)
    return APIResponse.success(data=result)


@router.get("/unread-count", response_model=APIResponse[int])
async def unread_count(
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    count = await get_unread_count(current_user.id, db)
    return APIResponse.success(data=count)


@router.post("/{notification_id}/read", response_model=APIResponse)
async def read_notification(
    notification_id: str,
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    notification = await mark_as_read(notification_id, db)
    if notification is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="通知不存在")
    return APIResponse.success(message="已标记为已读")


@router.post("/read-all", response_model=APIResponse)
async def read_all_notifications(
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    count = await mark_all_as_read(current_user.id, db)
    return APIResponse.success(message=f"已标记 {count} 条通知为已读")


@router.post("/send", response_model=APIResponse[NotificationInfo])
async def send_notification(
    data: NotificationCreate,
    current_user: User = Depends(require_role(UserRole.SUPER_ADMIN, UserRole.SCHOOL_ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    notification = await create_notification(data, current_user.id, db)
    return APIResponse.success(data=NotificationInfo.model_validate(notification))


@router.post("/batch-send", response_model=APIResponse)
async def batch_send_notification(
    data: NotificationBatchCreate,
    current_user: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db),
):
    notifications = await create_batch_notifications(data, current_user.id, db)
    return APIResponse.success(message=f"成功发送 {len(notifications)} 条通知")
