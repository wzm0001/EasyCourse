from typing import List, Optional
from datetime import datetime
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.log import SystemLog, LogType
from app.repositories.base import BaseRepository


class SystemLogRepository(BaseRepository[SystemLog]):
    def __init__(self, session: AsyncSession):
        super().__init__(SystemLog, session)

    async def get_by_type(self, log_type: LogType, page: int = 1, page_size: int = 20) -> tuple[List[SystemLog], int]:
        count_result = await self.session.execute(
            select(func.count()).select_from(SystemLog).where(SystemLog.log_type == log_type)
        )
        total = count_result.scalar_one()
        offset = (page - 1) * page_size
        result = await self.session.execute(
            select(SystemLog).where(SystemLog.log_type == log_type).order_by(SystemLog.created_at.desc()).offset(offset).limit(page_size)
        )
        items = list(result.scalars().all())
        return items, total

    async def get_by_user(self, user_id: str, page: int = 1, page_size: int = 20) -> tuple[List[SystemLog], int]:
        count_result = await self.session.execute(
            select(func.count()).select_from(SystemLog).where(SystemLog.user_id == user_id)
        )
        total = count_result.scalar_one()
        offset = (page - 1) * page_size
        result = await self.session.execute(
            select(SystemLog).where(SystemLog.user_id == user_id).order_by(SystemLog.created_at.desc()).offset(offset).limit(page_size)
        )
        items = list(result.scalars().all())
        return items, total

    async def get_by_school(self, school_id: str, page: int = 1, page_size: int = 20) -> tuple[List[SystemLog], int]:
        count_result = await self.session.execute(
            select(func.count()).select_from(SystemLog).where(SystemLog.school_id == school_id)
        )
        total = count_result.scalar_one()
        offset = (page - 1) * page_size
        result = await self.session.execute(
            select(SystemLog).where(SystemLog.school_id == school_id).order_by(SystemLog.created_at.desc()).offset(offset).limit(page_size)
        )
        items = list(result.scalars().all())
        return items, total

    async def get_by_date_range(self, start: datetime, end: datetime, page: int = 1, page_size: int = 20) -> tuple[List[SystemLog], int]:
        count_result = await self.session.execute(
            select(func.count()).select_from(SystemLog).where(
                SystemLog.created_at >= start,
                SystemLog.created_at <= end,
            )
        )
        total = count_result.scalar_one()
        offset = (page - 1) * page_size
        result = await self.session.execute(
            select(SystemLog).where(
                SystemLog.created_at >= start,
                SystemLog.created_at <= end,
            ).order_by(SystemLog.created_at.desc()).offset(offset).limit(page_size)
        )
        items = list(result.scalars().all())
        return items, total

    async def search_keyword(self, keyword: str, page: int = 1, page_size: int = 20) -> tuple[List[SystemLog], int]:
        pattern = f"%{keyword}%"
        count_result = await self.session.execute(
            select(func.count()).select_from(SystemLog).where(
                (SystemLog.action.ilike(pattern)) | (SystemLog.detail.ilike(pattern)) | (SystemLog.username.ilike(pattern))
            )
        )
        total = count_result.scalar_one()
        offset = (page - 1) * page_size
        result = await self.session.execute(
            select(SystemLog).where(
                (SystemLog.action.ilike(pattern)) | (SystemLog.detail.ilike(pattern)) | (SystemLog.username.ilike(pattern))
            ).order_by(SystemLog.created_at.desc()).offset(offset).limit(page_size)
        )
        items = list(result.scalars().all())
        return items, total
