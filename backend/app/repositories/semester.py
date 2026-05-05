from typing import Optional, List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.semester import Semester
from app.repositories.base import BaseRepository


class SemesterRepository(BaseRepository[Semester]):
    def __init__(self, session: AsyncSession):
        super().__init__(Semester, session)

    async def get_by_school(self, school_id: str, page: int = 1, page_size: int = 20) -> tuple[List[Semester], int]:
        count_result = await self.session.execute(
            select(func.count()).select_from(Semester).where(Semester.school_id == school_id)
        )
        total = count_result.scalar_one()
        offset = (page - 1) * page_size
        result = await self.session.execute(
            select(Semester)
            .where(Semester.school_id == school_id)
            .order_by(Semester.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        items = list(result.scalars().all())
        return items, total

    async def get_active(self, school_id: str) -> Optional[Semester]:
        result = await self.session.execute(
            select(Semester).where(Semester.school_id == school_id, Semester.is_active == True)
        )
        return result.scalar_one_or_none()

    async def get_archived(self, school_id: str, page: int = 1, page_size: int = 20) -> tuple[List[Semester], int]:
        count_result = await self.session.execute(
            select(func.count()).select_from(Semester)
            .where(Semester.school_id == school_id, Semester.is_archived == True)
        )
        total = count_result.scalar_one()
        offset = (page - 1) * page_size
        result = await self.session.execute(
            select(Semester)
            .where(Semester.school_id == school_id, Semester.is_archived == True)
            .order_by(Semester.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        items = list(result.scalars().all())
        return items, total
