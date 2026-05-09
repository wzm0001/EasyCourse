from typing import Optional, List
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.schedule import ScheduleCell, ScheduleLock
from app.models.constraint import ScheduleConstraint
from app.repositories.base import BaseRepository


class ScheduleCellRepository(BaseRepository[ScheduleCell]):
    def __init__(self, session: AsyncSession):
        super().__init__(ScheduleCell, session)

    async def get_by_class_semester(self, class_id: str, semester_id: str) -> List[ScheduleCell]:
        result = await self.session.execute(
            select(ScheduleCell).where(
                ScheduleCell.class_id == class_id,
                ScheduleCell.semester_id == semester_id,
            ).order_by(ScheduleCell.day_of_week, ScheduleCell.period_type, ScheduleCell.period_index)
        )
        return list(result.scalars().all())

    async def get_by_teacher_semester(self, teacher_id: str, semester_id: str) -> List[ScheduleCell]:
        result = await self.session.execute(
            select(ScheduleCell).where(
                ScheduleCell.teacher_id == teacher_id,
                ScheduleCell.semester_id == semester_id,
            ).order_by(ScheduleCell.day_of_week, ScheduleCell.period_type, ScheduleCell.period_index)
        )
        return list(result.scalars().all())

    async def get_by_classroom_semester(self, classroom_id: str, semester_id: str) -> List[ScheduleCell]:
        result = await self.session.execute(
            select(ScheduleCell).where(
                ScheduleCell.classroom_id == classroom_id,
                ScheduleCell.semester_id == semester_id,
            ).order_by(ScheduleCell.day_of_week, ScheduleCell.period_type, ScheduleCell.period_index)
        )
        return list(result.scalars().all())

    async def get_by_semester(self, school_id: str, semester_id: str) -> List[ScheduleCell]:
        result = await self.session.execute(
            select(ScheduleCell).where(
                ScheduleCell.school_id == school_id,
                ScheduleCell.semester_id == semester_id,
            ).order_by(ScheduleCell.day_of_week, ScheduleCell.period_type, ScheduleCell.period_index)
        )
        return list(result.scalars().all())

    async def get_cell(self, class_id: str, day_of_week: int, period_type: str, period_index: int, semester_id: str) -> Optional[ScheduleCell]:
        result = await self.session.execute(
            select(ScheduleCell).where(
                ScheduleCell.class_id == class_id,
                ScheduleCell.day_of_week == day_of_week,
                ScheduleCell.period_type == period_type,
                ScheduleCell.period_index == period_index,
                ScheduleCell.semester_id == semester_id,
            )
        )
        return result.scalar_one_or_none()

    async def delete_by_semester(self, school_id: str, semester_id: str, grade_id: Optional[str] = None) -> int:
        query = delete(ScheduleCell).where(
            ScheduleCell.school_id == school_id,
            ScheduleCell.semester_id == semester_id,
        )
        if grade_id:
            query = query.where(ScheduleCell.grade_id == grade_id)
        result = await self.session.execute(query)
        await self.session.flush()
        return result.rowcount

    async def get_by_grade_semester(self, grade_id: str, semester_id: str) -> List[ScheduleCell]:
        result = await self.session.execute(
            select(ScheduleCell).where(
                ScheduleCell.grade_id == grade_id,
                ScheduleCell.semester_id == semester_id,
            ).order_by(ScheduleCell.day_of_week, ScheduleCell.period_type, ScheduleCell.period_index)
        )
        return list(result.scalars().all())


class ScheduleLockRepository(BaseRepository[ScheduleLock]):
    def __init__(self, session: AsyncSession):
        super().__init__(ScheduleLock, session)

    async def get_by_semester(self, semester_id: str) -> Optional[ScheduleLock]:
        result = await self.session.execute(
            select(ScheduleLock).where(ScheduleLock.semester_id == semester_id)
        )
        return result.scalar_one_or_none()

    async def is_locked(self, semester_id: str) -> bool:
        lock = await self.get_by_semester(semester_id)
        return lock is not None


class ScheduleConstraintRepository(BaseRepository[ScheduleConstraint]):
    def __init__(self, session: AsyncSession):
        super().__init__(ScheduleConstraint, session)

    async def get_active_by_semester(self, school_id: str, semester_id: str) -> List[ScheduleConstraint]:
        result = await self.session.execute(
            select(ScheduleConstraint).where(
                ScheduleConstraint.school_id == school_id,
                ScheduleConstraint.semester_id == semester_id,
                ScheduleConstraint.is_active == True,
            )
        )
        return list(result.scalars().all())
