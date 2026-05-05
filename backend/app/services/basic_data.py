from typing import Optional, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.basic_data import (
    Grade, Class_, Course, GradeCourse, Teacher, TeacherCourse,
    Classroom, ClassroomCourse, TeachingArrangement,
)
from app.repositories.basic_data import (
    GradeRepository, ClassRepository, CourseRepository, GradeCourseRepository,
    TeacherRepository, TeacherCourseRepository, ClassroomRepository,
    ClassroomCourseRepository, TeachingArrangementRepository,
)


class GradeService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = GradeRepository(db)

    async def create(self, school_id: str, semester_id: str, data: dict) -> Grade:
        grade = Grade(
            school_id=school_id,
            semester_id=semester_id,
            name=data["name"],
            sort_order=data.get("sort_order", 0),
        )
        return await self.repo.create(grade)

    async def update(self, grade_id: str, data: dict) -> Optional[Grade]:
        update_data = {k: v for k, v in data.items() if v is not None}
        if not update_data:
            return await self.repo.get_by_id(grade_id)
        return await self.repo.update(grade_id, update_data)

    async def delete(self, grade_id: str) -> bool:
        class_repo = ClassRepository(self.db)
        classes, _ = await class_repo.get_by_grade(grade_id)
        if classes:
            return False
        grade_course_repo = GradeCourseRepository(self.db)
        grade_courses = await grade_course_repo.get_by_grade(grade_id)
        if grade_courses:
            return False
        return await self.repo.delete(grade_id)

    async def get_list(self, school_id: str, semester_id: str, page: int = 1, page_size: int = 20) -> tuple[List[Grade], int]:
        return await self.repo.get_by_semester(school_id, semester_id, page, page_size)

    async def get_by_id(self, grade_id: str) -> Optional[Grade]:
        return await self.repo.get_by_id(grade_id)


class ClassService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = ClassRepository(db)

    async def create(self, school_id: str, semester_id: str, data: dict) -> Class_:
        cls = Class_(
            school_id=school_id,
            semester_id=semester_id,
            grade_id=data["grade_id"],
            name=data["name"],
            teacher_id=data.get("teacher_id"),
            is_teaching_class=data.get("is_teaching_class", False),
        )
        return await self.repo.create(cls)

    async def update(self, class_id: str, data: dict) -> Optional[Class_]:
        update_data = {k: v for k, v in data.items() if v is not None}
        if not update_data:
            return await self.repo.get_by_id(class_id)
        return await self.repo.update(class_id, update_data)

    async def delete(self, class_id: str) -> bool:
        arrangement_repo = TeachingArrangementRepository(self.db)
        arrangements = await arrangement_repo.get_by_class(class_id)
        if arrangements:
            return False
        return await self.repo.delete(class_id)

    async def get_list(self, school_id: str, semester_id: str, grade_id: Optional[str] = None, page: int = 1, page_size: int = 20) -> tuple[List[Class_], int]:
        if grade_id:
            return await self.repo.get_by_grade(grade_id, page, page_size)
        return await self.repo.get_by_semester(school_id, semester_id, page, page_size)

    async def get_by_id(self, class_id: str) -> Optional[Class_]:
        return await self.repo.get_by_id(class_id)

    async def set_homeroom_teacher(self, class_id: str, teacher_id: Optional[str]) -> Optional[Class_]:
        return await self.repo.update(class_id, {"teacher_id": teacher_id})


class CourseService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = CourseRepository(db)

    async def create(self, school_id: str, data: dict) -> Course:
        course = Course(
            school_id=school_id,
            code=data["code"],
            name=data["name"],
            course_type=data.get("course_type", "required"),
            weekly_hours=data.get("weekly_hours", 1),
        )
        return await self.repo.create(course)

    async def update(self, course_id: str, data: dict) -> Optional[Course]:
        update_data = {k: v for k, v in data.items() if v is not None}
        if not update_data:
            return await self.repo.get_by_id(course_id)
        return await self.repo.update(course_id, update_data)

    async def delete(self, course_id: str) -> bool:
        arrangement_repo = TeachingArrangementRepository(self.db)
        result = await self.db.execute(
            select(TeachingArrangement).where(TeachingArrangement.course_id == course_id)
        )
        if result.scalars().first():
            return False
        grade_course_repo = GradeCourseRepository(self.db)
        gc_result = await self.db.execute(
            select(GradeCourse).where(GradeCourse.course_id == course_id)
        )
        if gc_result.scalars().first():
            return False
        return await self.repo.delete(course_id)

    async def get_list(self, school_id: str, page: int = 1, page_size: int = 20) -> tuple[List[Course], int]:
        return await self.repo.get_by_school(school_id, page, page_size)

    async def get_by_id(self, course_id: str) -> Optional[Course]:
        return await self.repo.get_by_id(course_id)


class GradeCourseService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = GradeCourseRepository(db)

    async def add_course_to_grade(self, school_id: str, semester_id: str, grade_id: str, course_id: str) -> GradeCourse:
        gc = GradeCourse(
            school_id=school_id,
            semester_id=semester_id,
            grade_id=grade_id,
            course_id=course_id,
        )
        return await self.repo.create(gc)

    async def remove_course_from_grade(self, grade_course_id: str) -> bool:
        return await self.repo.delete(grade_course_id)

    async def get_grade_courses(self, grade_id: str) -> List[GradeCourse]:
        return await self.repo.get_by_grade(grade_id)


class TeacherService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = TeacherRepository(db)

    async def create(self, school_id: str, semester_id: str, data: dict) -> Teacher:
        teacher = Teacher(
            school_id=school_id,
            semester_id=semester_id,
            user_id=data.get("user_id"),
            name=data["name"],
            employee_id=data["employee_id"],
            gender=data.get("gender", ""),
            phone=data.get("phone", ""),
            teaching_group=data.get("teaching_group", ""),
        )
        return await self.repo.create(teacher)

    async def update(self, teacher_id: str, data: dict) -> Optional[Teacher]:
        update_data = {k: v for k, v in data.items() if v is not None}
        if not update_data:
            return await self.repo.get_by_id(teacher_id)
        return await self.repo.update(teacher_id, update_data)

    async def delete(self, teacher_id: str) -> bool:
        arrangement_repo = TeachingArrangementRepository(self.db)
        arrangements = await arrangement_repo.get_by_teacher(teacher_id)
        if arrangements:
            return False
        return await self.repo.delete(teacher_id)

    async def get_list(self, school_id: str, semester_id: str, page: int = 1, page_size: int = 20) -> tuple[List[Teacher], int]:
        return await self.repo.get_by_semester(school_id, semester_id, page, page_size)

    async def get_by_id(self, teacher_id: str) -> Optional[Teacher]:
        return await self.repo.get_by_id(teacher_id)


class TeacherCourseService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = TeacherCourseRepository(db)

    async def add_course_to_teacher(self, school_id: str, semester_id: str, teacher_id: str, course_id: str) -> TeacherCourse:
        tc = TeacherCourse(
            school_id=school_id,
            semester_id=semester_id,
            teacher_id=teacher_id,
            course_id=course_id,
        )
        return await self.repo.create(tc)

    async def remove_course_from_teacher(self, teacher_course_id: str) -> bool:
        return await self.repo.delete(teacher_course_id)

    async def get_teacher_courses(self, teacher_id: str) -> List[TeacherCourse]:
        return await self.repo.get_by_teacher(teacher_id)


class ClassroomService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = ClassroomRepository(db)

    async def create(self, school_id: str, semester_id: str, data: dict) -> Classroom:
        classroom = Classroom(
            school_id=school_id,
            semester_id=semester_id,
            name=data["name"],
            room_type=data.get("room_type", "normal"),
            capacity=data.get("capacity", 50),
        )
        return await self.repo.create(classroom)

    async def update(self, classroom_id: str, data: dict) -> Optional[Classroom]:
        update_data = {k: v for k, v in data.items() if v is not None}
        if not update_data:
            return await self.repo.get_by_id(classroom_id)
        return await self.repo.update(classroom_id, update_data)

    async def delete(self, classroom_id: str) -> bool:
        return await self.repo.delete(classroom_id)

    async def get_list(self, school_id: str, semester_id: str, page: int = 1, page_size: int = 20) -> tuple[List[Classroom], int]:
        return await self.repo.get_by_semester(school_id, semester_id, page, page_size)

    async def get_by_id(self, classroom_id: str) -> Optional[Classroom]:
        return await self.repo.get_by_id(classroom_id)


class ClassroomCourseService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = ClassroomCourseRepository(db)

    async def add_course_to_classroom(self, school_id: str, semester_id: str, classroom_id: str, course_id: str) -> ClassroomCourse:
        cc = ClassroomCourse(
            school_id=school_id,
            semester_id=semester_id,
            classroom_id=classroom_id,
            course_id=course_id,
        )
        return await self.repo.create(cc)

    async def remove_course_from_classroom(self, classroom_course_id: str) -> bool:
        return await self.repo.delete(classroom_course_id)

    async def get_classroom_courses(self, classroom_id: str) -> List[ClassroomCourse]:
        return await self.repo.get_by_classroom(classroom_id)


class TeachingArrangementService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = TeachingArrangementRepository(db)

    async def create(self, school_id: str, semester_id: str, data: dict) -> TeachingArrangement:
        arrangement = TeachingArrangement(
            school_id=school_id,
            semester_id=semester_id,
            teacher_id=data["teacher_id"],
            course_id=data["course_id"],
            class_id=data["class_id"],
            weekly_hours=data.get("weekly_hours", 1),
        )
        return await self.repo.create(arrangement)

    async def update(self, arrangement_id: str, data: dict) -> Optional[TeachingArrangement]:
        update_data = {k: v for k, v in data.items() if v is not None}
        if not update_data:
            return await self.repo.get_by_id(arrangement_id)
        return await self.repo.update(arrangement_id, update_data)

    async def delete(self, arrangement_id: str) -> bool:
        return await self.repo.delete(arrangement_id)

    async def get_list(self, school_id: str, semester_id: str, page: int = 1, page_size: int = 20) -> tuple[List[TeachingArrangement], int]:
        return await self.repo.get_by_semester(school_id, semester_id, page, page_size)

    async def get_by_id(self, arrangement_id: str) -> Optional[TeachingArrangement]:
        return await self.repo.get_by_id(arrangement_id)
