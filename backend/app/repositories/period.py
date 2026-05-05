from typing import List, Optional
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.period import GradePeriodConfig, DayPeriodConfig, PeriodTemplate
from app.repositories.base import BaseRepository


class GradePeriodConfigRepository(BaseRepository[GradePeriodConfig]):
    def __init__(self, session: AsyncSession):
        super().__init__(GradePeriodConfig, session)

    async def get_by_grade_semester(self, grade_id: str, semester_id: str) -> List[GradePeriodConfig]:
        result = await self.session.execute(
            select(GradePeriodConfig).where(
                GradePeriodConfig.grade_id == grade_id,
                GradePeriodConfig.semester_id == semester_id,
            ).order_by(GradePeriodConfig.period_type, GradePeriodConfig.period_index)
        )
        return list(result.scalars().all())

    async def delete_by_grade_semester(self, grade_id: str, semester_id: str) -> None:
        await self.session.execute(
            delete(GradePeriodConfig).where(
                GradePeriodConfig.grade_id == grade_id,
                GradePeriodConfig.semester_id == semester_id,
            )
        )
        await self.session.flush()


class DayPeriodConfigRepository(BaseRepository[DayPeriodConfig]):
    def __init__(self, session: AsyncSession):
        super().__init__(DayPeriodConfig, session)

    async def get_by_grade_semester(self, grade_id: str, semester_id: str) -> List[DayPeriodConfig]:
        result = await self.session.execute(
            select(DayPeriodConfig).where(
                DayPeriodConfig.grade_id == grade_id,
                DayPeriodConfig.semester_id == semester_id,
            ).order_by(DayPeriodConfig.day_of_week, DayPeriodConfig.period_type, DayPeriodConfig.period_index)
        )
        return list(result.scalars().all())

    async def delete_by_grade_semester(self, grade_id: str, semester_id: str) -> None:
        await self.session.execute(
            delete(DayPeriodConfig).where(
                DayPeriodConfig.grade_id == grade_id,
                DayPeriodConfig.semester_id == semester_id,
            )
        )
        await self.session.flush()


class PeriodTemplateRepository(BaseRepository[PeriodTemplate]):
    def __init__(self, session: AsyncSession):
        super().__init__(PeriodTemplate, session)

    async def get_system_templates(self) -> List[PeriodTemplate]:
        result = await self.session.execute(
            select(PeriodTemplate).where(PeriodTemplate.is_system == True)
        )
        return list(result.scalars().all())

    async def get_custom_templates(self, school_id: str) -> List[PeriodTemplate]:
        result = await self.session.execute(
            select(PeriodTemplate).where(
                PeriodTemplate.is_system == False,
                PeriodTemplate.name != "",
            )
        )
        return list(result.scalars().all())
