from typing import Optional, List
from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.teaching_class import TeachingClass, TeachingClassMember
from app.repositories.base import BaseRepository


class TeachingClassRepository(BaseRepository[TeachingClass]):
    def __init__(self, session: AsyncSession):
        super().__init__(TeachingClass, session)

    async def get_by_grade(self, grade_id: str, semester_id: str, page: int = 1, page_size: int = 20) -> tuple[List[TeachingClass], int]:
        count_result = await self.session.execute(
            select(func.count()).select_from(TeachingClass).where(
                TeachingClass.grade_id == grade_id,
                TeachingClass.semester_id == semester_id,
            )
        )
        total = count_result.scalar_one()
        offset = (page - 1) * page_size
        result = await self.session.execute(
            select(TeachingClass).where(
                TeachingClass.grade_id == grade_id,
                TeachingClass.semester_id == semester_id,
            ).offset(offset).limit(page_size)
        )
        items = list(result.scalars().all())
        return items, total

    async def get_by_semester(self, school_id: str, semester_id: str, page: int = 1, page_size: int = 20) -> tuple[List[TeachingClass], int]:
        count_result = await self.session.execute(
            select(func.count()).select_from(TeachingClass).where(
                TeachingClass.school_id == school_id,
                TeachingClass.semester_id == semester_id,
            )
        )
        total = count_result.scalar_one()
        offset = (page - 1) * page_size
        result = await self.session.execute(
            select(TeachingClass).where(
                TeachingClass.school_id == school_id,
                TeachingClass.semester_id == semester_id,
            ).offset(offset).limit(page_size)
        )
        items = list(result.scalars().all())
        return items, total


class TeachingClassMemberRepository(BaseRepository[TeachingClassMember]):
    def __init__(self, session: AsyncSession):
        super().__init__(TeachingClassMember, session)

    async def get_by_teaching_class(self, teaching_class_id: str) -> List[TeachingClassMember]:
        result = await self.session.execute(
            select(TeachingClassMember).where(
                TeachingClassMember.teaching_class_id == teaching_class_id
            )
        )
        return list(result.scalars().all())

    async def get_by_class(self, class_id: str) -> List[TeachingClassMember]:
        result = await self.session.execute(
            select(TeachingClassMember).where(
                TeachingClassMember.class_id == class_id
            )
        )
        return list(result.scalars().all())

    async def delete_by_teaching_class(self, teaching_class_id: str) -> int:
        query = delete(TeachingClassMember).where(
            TeachingClassMember.teaching_class_id == teaching_class_id
        )
        result = await self.session.execute(query)
        await self.session.flush()
        return result.rowcount
