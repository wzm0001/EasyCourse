from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.constraint import ScheduleConstraint, ConstraintType
from app.repositories.base import BaseRepository


class ConstraintRepository(BaseRepository[ScheduleConstraint]):
    def __init__(self, session: AsyncSession):
        super().__init__(ScheduleConstraint, session)

    async def get_by_semester(
        self, school_id: str, semester_id: str, page: int = 1, page_size: int = 20
    ) -> tuple[List[ScheduleConstraint], int]:
        count_result = await self.session.execute(
            select(func.count()).select_from(ScheduleConstraint).where(
                ScheduleConstraint.school_id == school_id,
                ScheduleConstraint.semester_id == semester_id,
            )
        )
        total = count_result.scalar_one()
        offset = (page - 1) * page_size
        result = await self.session.execute(
            select(ScheduleConstraint).where(
                ScheduleConstraint.school_id == school_id,
                ScheduleConstraint.semester_id == semester_id,
            ).order_by(ScheduleConstraint.created_at.desc()).offset(offset).limit(page_size)
        )
        items = list(result.scalars().all())
        return items, total

    async def get_by_teacher(self, teacher_id: str) -> List[ScheduleConstraint]:
        result = await self.session.execute(
            select(ScheduleConstraint).where(ScheduleConstraint.teacher_id == teacher_id)
        )
        return list(result.scalars().all())

    async def get_by_course(self, course_id: str) -> List[ScheduleConstraint]:
        result = await self.session.execute(
            select(ScheduleConstraint).where(ScheduleConstraint.course_id == course_id)
        )
        return list(result.scalars().all())

    async def get_active_constraints(self, school_id: str, semester_id: str) -> List[ScheduleConstraint]:
        result = await self.session.execute(
            select(ScheduleConstraint).where(
                ScheduleConstraint.school_id == school_id,
                ScheduleConstraint.semester_id == semester_id,
                ScheduleConstraint.is_active == True,
            ).order_by(ScheduleConstraint.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_type(
        self, constraint_type: ConstraintType, school_id: str, semester_id: str
    ) -> List[ScheduleConstraint]:
        result = await self.session.execute(
            select(ScheduleConstraint).where(
                ScheduleConstraint.constraint_type == constraint_type,
                ScheduleConstraint.school_id == school_id,
                ScheduleConstraint.semester_id == semester_id,
            ).order_by(ScheduleConstraint.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_semester_and_type(
        self, school_id: str, semester_id: str, constraint_type: ConstraintType, page: int = 1, page_size: int = 20
    ) -> tuple[List[ScheduleConstraint], int]:
        count_result = await self.session.execute(
            select(func.count()).select_from(ScheduleConstraint).where(
                ScheduleConstraint.school_id == school_id,
                ScheduleConstraint.semester_id == semester_id,
                ScheduleConstraint.constraint_type == constraint_type,
            )
        )
        total = count_result.scalar_one()
        offset = (page - 1) * page_size
        result = await self.session.execute(
            select(ScheduleConstraint).where(
                ScheduleConstraint.school_id == school_id,
                ScheduleConstraint.semester_id == semester_id,
                ScheduleConstraint.constraint_type == constraint_type,
            ).order_by(ScheduleConstraint.created_at.desc()).offset(offset).limit(page_size)
        )
        items = list(result.scalars().all())
        return items, total
