from typing import Optional, List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.basic_data import (
    Grade, Class_, Course, GradeCourse, Teacher, TeacherCourse,
    Classroom, ClassroomCourse, TeachingArrangement,
)
from app.repositories.base import BaseRepository


class GradeRepository(BaseRepository[Grade]):
    def __init__(self, session: AsyncSession):
        super().__init__(Grade, session)

    async def get_by_semester(self, school_id: str, semester_id: str, page: int = 1, page_size: int = 20) -> tuple[List[Grade], int]:
        count_result = await self.session.execute(
            select(func.count()).select_from(Grade).where(
                Grade.school_id == school_id,
                Grade.semester_id == semester_id,
            )
        )
        total = count_result.scalar_one()
        offset = (page - 1) * page_size
        result = await self.session.execute(
            select(Grade).where(
                Grade.school_id == school_id,
                Grade.semester_id == semester_id,
            ).order_by(Grade.sort_order).offset(offset).limit(page_size)
        )
        items = list(result.scalars().all())
        return items, total


class ClassRepository(BaseRepository[Class_]):
    def __init__(self, session: AsyncSession):
        super().__init__(Class_, session)

    async def get_by_grade(self, grade_id: str, page: int = 1, page_size: int = 20) -> tuple[List[Class_], int]:
        count_result = await self.session.execute(
            select(func.count()).select_from(Class_).where(Class_.grade_id == grade_id)
        )
        total = count_result.scalar_one()
        offset = (page - 1) * page_size
        result = await self.session.execute(
            select(Class_).where(Class_.grade_id == grade_id).offset(offset).limit(page_size)
        )
        items = list(result.scalars().all())
        return items, total

    async def get_by_semester(self, school_id: str, semester_id: str, page: int = 1, page_size: int = 20) -> tuple[List[Class_], int]:
        count_result = await self.session.execute(
            select(func.count()).select_from(Class_).where(
                Class_.school_id == school_id,
                Class_.semester_id == semester_id,
            )
        )
        total = count_result.scalar_one()
        offset = (page - 1) * page_size
        result = await self.session.execute(
            select(Class_).where(
                Class_.school_id == school_id,
                Class_.semester_id == semester_id,
            ).offset(offset).limit(page_size)
        )
        items = list(result.scalars().all())
        return items, total

    async def get_by_teacher(self, teacher_id: str) -> List[Class_]:
        result = await self.session.execute(
            select(Class_).where(Class_.teacher_id == teacher_id)
        )
        return list(result.scalars().all())


class CourseRepository(BaseRepository[Course]):
    def __init__(self, session: AsyncSession):
        super().__init__(Course, session)

    async def get_by_school(self, school_id: str, page: int = 1, page_size: int = 20) -> tuple[List[Course], int]:
        count_result = await self.session.execute(
            select(func.count()).select_from(Course).where(Course.school_id == school_id)
        )
        total = count_result.scalar_one()
        offset = (page - 1) * page_size
        result = await self.session.execute(
            select(Course).where(Course.school_id == school_id).offset(offset).limit(page_size)
        )
        items = list(result.scalars().all())
        return items, total


class GradeCourseRepository(BaseRepository[GradeCourse]):
    def __init__(self, session: AsyncSession):
        super().__init__(GradeCourse, session)

    async def get_by_grade(self, grade_id: str) -> List[GradeCourse]:
        result = await self.session.execute(
            select(GradeCourse).where(GradeCourse.grade_id == grade_id)
        )
        return list(result.scalars().all())

    async def get_by_semester(self, school_id: str, semester_id: str) -> List[GradeCourse]:
        result = await self.session.execute(
            select(GradeCourse).where(
                GradeCourse.school_id == school_id,
                GradeCourse.semester_id == semester_id,
            )
        )
        return list(result.scalars().all())


class TeacherRepository(BaseRepository[Teacher]):
    def __init__(self, session: AsyncSession):
        super().__init__(Teacher, session)

    async def get_by_semester(self, school_id: str, semester_id: str, page: int = 1, page_size: int = 20) -> tuple[List[Teacher], int]:
        count_result = await self.session.execute(
            select(func.count()).select_from(Teacher).where(
                Teacher.school_id == school_id,
                Teacher.semester_id == semester_id,
            )
        )
        total = count_result.scalar_one()
        offset = (page - 1) * page_size
        result = await self.session.execute(
            select(Teacher).where(
                Teacher.school_id == school_id,
                Teacher.semester_id == semester_id,
            ).offset(offset).limit(page_size)
        )
        items = list(result.scalars().all())
        return items, total

    async def get_by_employee_id(self, employee_id: str, school_id: str) -> Optional[Teacher]:
        result = await self.session.execute(
            select(Teacher).where(
                Teacher.employee_id == employee_id,
                Teacher.school_id == school_id,
            )
        )
        return result.scalar_one_or_none()


class TeacherCourseRepository(BaseRepository[TeacherCourse]):
    def __init__(self, session: AsyncSession):
        super().__init__(TeacherCourse, session)

    async def get_by_teacher(self, teacher_id: str) -> List[TeacherCourse]:
        result = await self.session.execute(
            select(TeacherCourse).where(TeacherCourse.teacher_id == teacher_id)
        )
        return list(result.scalars().all())

    async def get_by_semester(self, school_id: str, semester_id: str) -> List[TeacherCourse]:
        result = await self.session.execute(
            select(TeacherCourse).where(
                TeacherCourse.school_id == school_id,
                TeacherCourse.semester_id == semester_id,
            )
        )
        return list(result.scalars().all())


class ClassroomRepository(BaseRepository[Classroom]):
    def __init__(self, session: AsyncSession):
        super().__init__(Classroom, session)

    async def get_by_semester(self, school_id: str, semester_id: str, page: int = 1, page_size: int = 20) -> tuple[List[Classroom], int]:
        count_result = await self.session.execute(
            select(func.count()).select_from(Classroom).where(
                Classroom.school_id == school_id,
                Classroom.semester_id == semester_id,
            )
        )
        total = count_result.scalar_one()
        offset = (page - 1) * page_size
        result = await self.session.execute(
            select(Classroom).where(
                Classroom.school_id == school_id,
                Classroom.semester_id == semester_id,
            ).offset(offset).limit(page_size)
        )
        items = list(result.scalars().all())
        return items, total

    async def get_by_type(self, room_type: str, school_id: str, semester_id: str) -> List[Classroom]:
        result = await self.session.execute(
            select(Classroom).where(
                Classroom.room_type == room_type,
                Classroom.school_id == school_id,
                Classroom.semester_id == semester_id,
            )
        )
        return list(result.scalars().all())


class ClassroomCourseRepository(BaseRepository[ClassroomCourse]):
    def __init__(self, session: AsyncSession):
        super().__init__(ClassroomCourse, session)

    async def get_by_classroom(self, classroom_id: str) -> List[ClassroomCourse]:
        result = await self.session.execute(
            select(ClassroomCourse).where(ClassroomCourse.classroom_id == classroom_id)
        )
        return list(result.scalars().all())

    async def get_by_semester(self, school_id: str, semester_id: str) -> List[ClassroomCourse]:
        result = await self.session.execute(
            select(ClassroomCourse).where(
                ClassroomCourse.school_id == school_id,
                ClassroomCourse.semester_id == semester_id,
            )
        )
        return list(result.scalars().all())


class TeachingArrangementRepository(BaseRepository[TeachingArrangement]):
    def __init__(self, session: AsyncSession):
        super().__init__(TeachingArrangement, session)

    async def get_by_semester(self, school_id: str, semester_id: str, page: int = 1, page_size: int = 20) -> tuple[List[TeachingArrangement], int]:
        count_result = await self.session.execute(
            select(func.count()).select_from(TeachingArrangement).where(
                TeachingArrangement.school_id == school_id,
                TeachingArrangement.semester_id == semester_id,
            )
        )
        total = count_result.scalar_one()
        offset = (page - 1) * page_size
        result = await self.session.execute(
            select(TeachingArrangement).where(
                TeachingArrangement.school_id == school_id,
                TeachingArrangement.semester_id == semester_id,
            ).offset(offset).limit(page_size)
        )
        items = list(result.scalars().all())
        return items, total

    async def get_by_teacher(self, teacher_id: str) -> List[TeachingArrangement]:
        result = await self.session.execute(
            select(TeachingArrangement).where(TeachingArrangement.teacher_id == teacher_id)
        )
        return list(result.scalars().all())

    async def get_by_class(self, class_id: str) -> List[TeachingArrangement]:
        result = await self.session.execute(
            select(TeachingArrangement).where(TeachingArrangement.class_id == class_id)
        )
        return list(result.scalars().all())
