from typing import List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.notification import Notification
from app.repositories.base import BaseRepository


class NotificationRepository(BaseRepository[Notification]):
    def __init__(self, session: AsyncSession):
        super().__init__(Notification, session)

    async def get_by_receiver(self, receiver_id: str, page: int = 1, page_size: int = 20) -> tuple[List[Notification], int]:
        count_result = await self.session.execute(
            select(func.count()).select_from(Notification).where(Notification.receiver_id == receiver_id)
        )
        total = count_result.scalar_one()
        offset = (page - 1) * page_size
        result = await self.session.execute(
            select(Notification).where(Notification.receiver_id == receiver_id).order_by(Notification.created_at.desc()).offset(offset).limit(page_size)
        )
        items = list(result.scalars().all())
        return items, total

    async def get_unread(self, receiver_id: str, page: int = 1, page_size: int = 20) -> tuple[List[Notification], int]:
        count_result = await self.session.execute(
            select(func.count()).select_from(Notification).where(
                Notification.receiver_id == receiver_id,
                Notification.is_read == False,
            )
        )
        total = count_result.scalar_one()
        offset = (page - 1) * page_size
        result = await self.session.execute(
            select(Notification).where(
                Notification.receiver_id == receiver_id,
                Notification.is_read == False,
            ).order_by(Notification.created_at.desc()).offset(offset).limit(page_size)
        )
        items = list(result.scalars().all())
        return items, total

    async def get_by_school(self, school_id: str, page: int = 1, page_size: int = 20) -> tuple[List[Notification], int]:
        count_result = await self.session.execute(
            select(func.count()).select_from(Notification).where(Notification.school_id == school_id)
        )
        total = count_result.scalar_one()
        offset = (page - 1) * page_size
        result = await self.session.execute(
            select(Notification).where(Notification.school_id == school_id).order_by(Notification.created_at.desc()).offset(offset).limit(page_size)
        )
        items = list(result.scalars().all())
        return items, total

    async def count_unread(self, receiver_id: str) -> int:
        result = await self.session.execute(
            select(func.count()).select_from(Notification).where(
                Notification.receiver_id == receiver_id,
                Notification.is_read == False,
            )
        )
        return result.scalar_one()
