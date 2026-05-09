import secrets
import string
from typing import Optional, List

from sqlalchemy import select, func
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
            morning_reading_count=data.get("morning_reading_count", 1),
            regular_class_count=data.get("regular_class_count", 8),
            evening_study_count=data.get("evening_study_count", 0),
        )
        return await self.repo.create(grade)

    async def update(self, grade_id: str, data: dict) -> Optional[Grade]:
        update_data = {k: v for k, v in data.items() if v is not None}
        if not update_data:
            return await self.repo.get_by_id(grade_id)
        return await self.repo.update(grade_id, update_data)

    async def delete(self, grade_id: str) -> bool:
        from app.models.schedule import ScheduleCell

        class_repo = ClassRepository(self.db)
        classes, _ = await class_repo.get_by_grade(grade_id)
        if classes:
            return False
        schedule_result = await self.db.execute(
            select(ScheduleCell).where(ScheduleCell.grade_id == grade_id)
        )
        if schedule_result.scalars().first():
            raise ValueError("该年级存在排课记录，无法删除，请先清除排课数据")
        grade_course_repo = GradeCourseRepository(self.db)
        grade_courses = await grade_course_repo.get_by_grade(grade_id)
        for gc in grade_courses:
            await grade_course_repo.delete(gc.id)
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
            classroom_id=data.get("classroom_id"),
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

    async def _generate_code(self, school_id: str) -> str:
        result = await self.db.execute(
            select(func.count()).select_from(Course).where(Course.school_id == school_id)
        )
        count = result.scalar_one() + 1
        return f"C{count:04d}"

    async def create(self, school_id: str, data: dict) -> Course:
        code = data.get("code") or await self._generate_code(school_id)
        course = Course(
            school_id=school_id,
            code=code,
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

    async def get_or_create_by_name(self, school_id: str, name: str) -> Course:
        result = await self.db.execute(
            select(Course).where(Course.school_id == school_id, Course.name == name)
        )
        course = result.scalar_one_or_none()
        if course:
            if not course.code:
                course.code = await self._generate_code(school_id)
                await self.db.flush()
            return course
        code = await self._generate_code(school_id)
        course = Course(school_id=school_id, code=code, name=name)
        return await self.repo.create(course)


class GradeCourseService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = GradeCourseRepository(db)

    async def add_course_to_grade(self, school_id: str, semester_id: str, grade_id: str, course_id: str, weekly_hours: int = 1, period_type: str = "regular") -> GradeCourse:
        gc = GradeCourse(
            school_id=school_id,
            semester_id=semester_id,
            grade_id=grade_id,
            course_id=course_id,
            weekly_hours=weekly_hours,
            period_type=period_type,
        )
        return await self.repo.create(gc)

    async def batch_add_courses_to_grade(self, school_id: str, semester_id: str, grade_id: str, courses: list, period_type: str = "regular") -> list:
        course_service = CourseService(self.db)
        results = []
        for item in courses:
            course = await course_service.get_or_create_by_name(school_id, item["name"])
            existing = await self.db.execute(
                select(GradeCourse).where(
                    GradeCourse.grade_id == grade_id,
                    GradeCourse.course_id == course.id,
                    GradeCourse.period_type == period_type,
                )
            )
            if existing.scalar_one_or_none():
                continue
            gc = GradeCourse(
                school_id=school_id,
                semester_id=semester_id,
                grade_id=grade_id,
                course_id=course.id,
                weekly_hours=item.get("weekly_hours", 1),
                period_type=period_type,
            )
            gc = await self.repo.create(gc)
            results.append(gc)
        return results

    async def update_grade_course(self, grade_course_id: str, weekly_hours: Optional[int] = None, period_type: Optional[str] = None) -> Optional[GradeCourse]:
        update_data = {}
        if weekly_hours is not None:
            update_data["weekly_hours"] = weekly_hours
        if period_type is not None:
            update_data["period_type"] = period_type
        if update_data:
            return await self.repo.update(grade_course_id, update_data)
        return await self.repo.get_by_id(grade_course_id)

    async def remove_course_from_grade(self, grade_course_id: str) -> bool:
        return await self.repo.delete(grade_course_id)

    async def get_grade_courses(self, grade_id: str, period_type: Optional[str] = None) -> List[GradeCourse]:
        return await self.repo.get_by_grade(grade_id, period_type)


class TeacherService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = TeacherRepository(db)

    async def create(self, school_id: str, semester_id: str, data: dict) -> Teacher:
        from app.models.user import User, UserRole
        from app.services.auth import get_password_hash
        from app.repositories.user import UserRepository

        user_repo = UserRepository(self.db)
        username = data["name"]
        existing_user = await user_repo.get_by_username(username)
        if existing_user:
            raise ValueError(f"用户名「{username}」已存在，请使用不同的教师姓名")
        phone = data.get("phone", "")
        email = data.get("email", "")
        password = phone if phone else self._generate_default_password()
        user = User(
            username=username,
            password_hash=get_password_hash(password),
            real_name=data["name"],
            role=UserRole.TEACHER,
            school_id=school_id,
            phone=phone,
            email=email,
            is_active=True,
            must_change_password=True,
        )
        user = await user_repo.create(user)

        teacher = Teacher(
            school_id=school_id,
            semester_id=semester_id,
            user_id=user.id,
            name=data["name"],
            employee_id=data.get("employee_id", ""),
            gender=data.get("gender", ""),
            phone=phone,
            teaching_group=data.get("teaching_group", ""),
            specialization=data.get("specialization", ""),
        )
        return await self.repo.create(teacher)

    @staticmethod
    def _generate_default_password() -> str:
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(12))

    async def update(self, teacher_id: str, data: dict) -> Optional[Teacher]:
        update_data = {k: v for k, v in data.items() if v is not None}
        if "user_id" in update_data:
            del update_data["user_id"]
        teacher = await self.repo.get_by_id(teacher_id)
        if not teacher:
            return None
        if update_data:
            teacher = await self.repo.update(teacher_id, update_data)
        if teacher and teacher.user_id:
            from app.repositories.user import UserRepository
            user_repo = UserRepository(self.db)
            user_update = {}
            if "name" in data and data["name"] is not None:
                user_update["username"] = data["name"]
                user_update["real_name"] = data["name"]
            if "phone" in data and data["phone"] is not None:
                user_update["phone"] = data["phone"]
            if user_update:
                await user_repo.update(teacher.user_id, user_update)
        return teacher

    async def delete(self, teacher_id: str) -> bool:
        from sqlalchemy import delete as sa_delete
        from app.models.basic_data import TeacherCourse, TeachingArrangement, Class_, Grade
        from app.models.schedule import ScheduleCell
        from app.models.teaching_class import TeachingClass

        await self.db.execute(
            sa_delete(ScheduleCell).where(ScheduleCell.teacher_id == teacher_id)
        )
        await self.db.execute(
            sa_delete(TeachingArrangement).where(TeachingArrangement.teacher_id == teacher_id)
        )
        await self.db.execute(
            sa_delete(TeacherCourse).where(TeacherCourse.teacher_id == teacher_id)
        )
        await self.db.execute(
            sa_delete(TeachingClass).where(TeachingClass.teacher_id == teacher_id)
        )

        classes_result = await self.db.execute(
            select(Class_).where(Class_.head_teacher_id == teacher_id)
        )
        for cls in classes_result.scalars().all():
            cls.head_teacher_id = None
        await self.db.flush()

        grades_result = await self.db.execute(
            select(Grade).where(Grade.grade_leader_id == teacher_id)
        )
        for grade in grades_result.scalars().all():
            grade.grade_leader_id = None
        await self.db.flush()

        teacher = await self.repo.get_by_id(teacher_id)
        if teacher and teacher.user_id:
            from app.repositories.user import UserRepository
            user_repo = UserRepository(self.db)
            await user_repo.delete(teacher.user_id)
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

    async def _generate_code(self, school_id: str, semester_id: str) -> str:
        result = await self.db.execute(
            select(func.count()).select_from(Classroom).where(
                Classroom.school_id == school_id,
                Classroom.semester_id == semester_id,
            )
        )
        count = result.scalar_one() + 1
        return f"CR{count:05d}"

    async def create(self, school_id: str, semester_id: str, data: dict) -> Classroom:
        code = await self._generate_code(school_id, semester_id)
        classroom = Classroom(
            school_id=school_id,
            semester_id=semester_id,
            building_name=data["building_name"],
            room_number=data["room_number"],
            code=code,
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

    async def get_list(self, school_id: str, semester_id: str, page: int = 1, page_size: int = 20, building_name: Optional[str] = None, room_type: Optional[str] = None) -> tuple[List[Classroom], int]:
        return await self.repo.get_by_semester(school_id, semester_id, page, page_size, building_name, room_type)

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
            continuous_hours=data.get("continuous_hours", 1),
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


class QuickSetupService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def quick_setup(self, school_id: str, semester_id: str, data: dict) -> dict:
        grade_service = GradeService(self.db)
        class_service = ClassService(self.db)
        classroom_service = ClassroomService(self.db)

        grade = await grade_service.create(school_id, semester_id, {
            "name": data["grade_name"],
            "morning_reading_count": data.get("morning_reading_count", 1),
            "regular_class_count": data.get("regular_class_count", 8),
            "evening_study_count": data.get("evening_study_count", 0),
        })

        class_ids = []
        classroom_ids = []
        classroom_names = data.get("classroom_names") or []

        for i, class_name in enumerate(data["class_names"]):
            classroom_id = None
            if i < len(classroom_names):
                name_parts = classroom_names[i].rsplit(" ", 1) if " " in classroom_names[i] else (classroom_names[i], "")
                building_name = name_parts[0]
                room_number = name_parts[1] if len(name_parts) > 1 else "00"
                classroom = await classroom_service.create(school_id, semester_id, {
                    "building_name": building_name,
                    "room_number": room_number,
                })
                classroom_ids.append(classroom.id)
                classroom_id = classroom.id

            cls = await class_service.create(school_id, semester_id, {
                "grade_id": grade.id,
                "name": class_name,
                "classroom_id": classroom_id,
            })
            class_ids.append(cls.id)

        return {
            "grade_id": grade.id,
            "class_ids": class_ids,
            "classroom_ids": classroom_ids,
        }

    async def batch_create_arrangements(self, school_id: str, semester_id: str, arrangements: list) -> list:
        arrangement_service = TeachingArrangementService(self.db)
        results = []
        for arr_data in arrangements:
            arr = await arrangement_service.create(school_id, semester_id, arr_data)
            results.append(arr)
        return results
