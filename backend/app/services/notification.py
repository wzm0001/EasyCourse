from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.notification import Notification, NotificationType
from app.models.user import User, UserRole
from app.repositories.notification import NotificationRepository
from app.schemas.notification import NotificationCreate, NotificationBatchCreate, NotificationInfo
from app.schemas.common import PageResponse


async def create_notification(data: NotificationCreate, sender_id: Optional[str], db: AsyncSession) -> Notification:
    repo = NotificationRepository(db)
    notification = Notification(
        school_id=data.school_id,
        type=data.type,
        title=data.title,
        content=data.content,
        sender_id=sender_id,
        receiver_id=data.receiver_id,
    )
    notification = await repo.create(notification)
    return notification


async def create_batch_notifications(data: NotificationBatchCreate, sender_id: Optional[str], db: AsyncSession) -> list[Notification]:
    repo = NotificationRepository(db)
    notifications = []
    for receiver_id in data.receiver_ids:
        notification = Notification(
            school_id=data.school_id,
            type=data.type,
            title=data.title,
            content=data.content,
            sender_id=sender_id,
            receiver_id=receiver_id,
        )
        notification = await repo.create(notification)
        notifications.append(notification)
    return notifications


async def get_notifications(receiver_id: str, page: int, page_size: int, db: AsyncSession) -> PageResponse[NotificationInfo]:
    repo = NotificationRepository(db)
    items, total = await repo.get_by_receiver(receiver_id, page=page, page_size=page_size)
    notification_infos = [NotificationInfo.model_validate(n) for n in items]
    return PageResponse(items=notification_infos, total=total, page=page, page_size=page_size)


async def get_unread_count(receiver_id: str, db: AsyncSession) -> int:
    repo = NotificationRepository(db)
    return await repo.count_unread(receiver_id)


async def mark_as_read(notification_id: str, db: AsyncSession) -> Optional[Notification]:
    repo = NotificationRepository(db)
    notification = await repo.get_by_id(notification_id)
    if notification is None:
        return None
    await repo.update(notification_id, {"is_read": True})
    return await repo.get_by_id(notification_id)


async def mark_all_as_read(receiver_id: str, db: AsyncSession) -> int:
    from sqlalchemy import update
    stmt = update(Notification).where(
        Notification.receiver_id == receiver_id,
        Notification.is_read == False,
    ).values(is_read=True)
    result = await db.execute(stmt)
    await db.flush()
    return result.rowcount


async def send_approval_result(approval_id: str, approved: bool, reject_reason: Optional[str], db: AsyncSession) -> Notification:
    from app.repositories.user import ApprovalRepository
    approval_repo = ApprovalRepository(db)
    record = await approval_repo.get_by_id(approval_id)
    if record is None:
        raise ValueError("审批记录不存在")
    title = "审批通过" if approved else "审批被拒绝"
    content = f"您的申请已通过" if approved else f"您的申请被拒绝，原因：{reject_reason or '无'}"
    data = NotificationCreate(
        type=NotificationType.APPROVAL_RESULT,
        title=title,
        content=content,
        receiver_id=record.requester_id,
        school_id=record.school_id,
    )
    return await create_notification(data, None, db)


async def send_schedule_complete(user_id: str, result: str, db: AsyncSession) -> Notification:
    data = NotificationCreate(
        type=NotificationType.SCHEDULE_COMPLETE,
        title="排课完成",
        content=result,
        receiver_id=user_id,
    )
    return await create_notification(data, None, db)


async def send_system_maintenance(title: str, content: str, school_id: Optional[str], db: AsyncSession) -> list[Notification]:
    from sqlalchemy import select
    query = select(User)
    if school_id:
        query = query.where(User.school_id == school_id)
    query_result = await db.execute(query)
    users = list(query_result.scalars().all())
    receiver_ids = [u.id for u in users]
    data = NotificationBatchCreate(
        type=NotificationType.SYSTEM_MAINTENANCE,
        title=title,
        content=content,
        receiver_ids=receiver_ids,
        school_id=school_id,
    )
    return await create_batch_notifications(data, None, db)


async def send_school_registration_notification(school_name: str, school_id: str, db: AsyncSession) -> list[Notification]:
    from sqlalchemy import select
    query_result = await db.execute(
        select(User).where(User.role == UserRole.SUPER_ADMIN, User.is_active == True)
    )
    super_admins = list(query_result.scalars().all())
    if not super_admins:
        return []
    receiver_ids = [u.id for u in super_admins]
    data = NotificationBatchCreate(
        type=NotificationType.SCHOOL_REGISTRATION,
        title="新学校注册申请",
        content=f"学校「{school_name}」提交了注册申请，请前往审批管理进行处理。",
        receiver_ids=receiver_ids,
        school_id=school_id,
    )
    return await create_batch_notifications(data, None, db)
