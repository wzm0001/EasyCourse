from typing import Optional, List

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.constraint import ScheduleConstraint, ConstraintType
from app.models.basic_data import Teacher, Course, Classroom, Grade
from app.repositories.constraint import ConstraintRepository
from app.repositories.basic_data import TeacherRepository, CourseRepository, ClassroomRepository, GradeRepository
from app.schemas.constraint import ConstraintCreate, ConstraintUpdate, ConstraintInfo
from app.schemas.common import PageResponse


async def validate_constraint(data: ConstraintCreate, db: AsyncSession) -> Optional[str]:
    ct = data.constraint_type
    if ct == ConstraintType.TEACHER_UNAVAILABLE:
        if not data.teacher_id:
            return "教师不可排课时段必须指定教师"
        if data.day_of_week is None:
            return "教师不可排课时段必须指定星期"
        if not data.period_type:
            return "教师不可排课时段必须指定时段类型"
        if data.period_index is None:
            return "教师不可排课时段必须指定节次"
    elif ct == ConstraintType.COURSE_PERIOD_LIMIT:
        if not data.course_id:
            return "课程时段限制必须指定课程"
        if data.day_of_week is None:
            return "课程时段限制必须指定星期"
        if not data.period_type:
            return "课程时段限制必须指定时段类型"
        if data.period_index is None:
            return "课程时段限制必须指定节次"
    elif ct == ConstraintType.COURSE_CONTINUOUS:
        if not data.course_id:
            return "课程连续性必须指定课程"
        if data.allow_continuous is None:
            return "课程连续性必须指定是否允许连排"
    elif ct == ConstraintType.COURSE_SCATTER:
        if not data.course_id:
            return "课程分散性必须指定课程"
        if data.require_scatter is None:
            return "课程分散性必须指定是否要求分散"
    elif ct == ConstraintType.CLASSROOM_RESTRICTION:
        if not data.course_id:
            return "教室限制必须指定课程"
        if not data.classroom_id:
            return "教室限制必须指定教室"
    elif ct == ConstraintType.TEACHER_DAILY_LIMIT:
        if not data.teacher_id:
            return "教师日课时上限必须指定教师"
        if data.max_daily_hours is None:
            return "教师日课时上限必须指定最大日课时数"
    return None


async def _build_constraint_info(constraint: ScheduleConstraint, db: AsyncSession) -> ConstraintInfo:
    teacher_name = None
    course_name = None
    classroom_name = None
    grade_name = None

    if constraint.teacher_id:
        teacher_repo = TeacherRepository(db)
        teacher = await teacher_repo.get_by_id(constraint.teacher_id)
        teacher_name = teacher.name if teacher else None

    if constraint.course_id:
        course_repo = CourseRepository(db)
        course = await course_repo.get_by_id(constraint.course_id)
        course_name = course.name if course else None

    if constraint.classroom_id:
        classroom_repo = ClassroomRepository(db)
        classroom = await classroom_repo.get_by_id(constraint.classroom_id)
        classroom_name = f"{classroom.building_name} {classroom.room_number}" if classroom else None

    if constraint.grade_id:
        grade_repo = GradeRepository(db)
        grade = await grade_repo.get_by_id(constraint.grade_id)
        grade_name = grade.name if grade else None

    return ConstraintInfo(
        id=constraint.id,
        school_id=constraint.school_id,
        semester_id=constraint.semester_id,
        constraint_type=constraint.constraint_type,
        priority=constraint.priority,
        is_active=constraint.is_active,
        teacher_id=constraint.teacher_id,
        teacher_name=teacher_name,
        course_id=constraint.course_id,
        course_name=course_name,
        classroom_id=constraint.classroom_id,
        classroom_name=classroom_name,
        grade_id=constraint.grade_id,
        grade_name=grade_name,
        day_of_week=constraint.day_of_week,
        period_type=constraint.period_type,
        period_index=constraint.period_index,
        max_daily_hours=constraint.max_daily_hours,
        allow_continuous=constraint.allow_continuous,
        require_scatter=constraint.require_scatter,
        description=constraint.description,
        created_at=constraint.created_at,
    )


async def create_constraint(
    data: ConstraintCreate, school_id: str, semester_id: str, db: AsyncSession
) -> ConstraintInfo:
    error = await validate_constraint(data, db)
    if error:
        raise ValueError(error)

    repo = ConstraintRepository(db)
    constraint = ScheduleConstraint(
        school_id=school_id,
        semester_id=semester_id,
        constraint_type=data.constraint_type,
        priority=data.priority,
        is_active=data.is_active,
        teacher_id=data.teacher_id,
        course_id=data.course_id,
        classroom_id=data.classroom_id,
        grade_id=data.grade_id,
        day_of_week=data.day_of_week,
        period_type=data.period_type,
        period_index=data.period_index,
        max_daily_hours=data.max_daily_hours,
        allow_continuous=data.allow_continuous,
        require_scatter=data.require_scatter,
        description=data.description,
    )
    constraint = await repo.create(constraint)
    return await _build_constraint_info(constraint, db)


async def update_constraint(
    constraint_id: str, data: ConstraintUpdate, db: AsyncSession
) -> Optional[ConstraintInfo]:
    repo = ConstraintRepository(db)
    constraint = await repo.get_by_id(constraint_id)
    if constraint is None:
        return None
    update_data = data.model_dump(exclude_unset=True)
    if update_data:
        await repo.update(constraint_id, update_data)
    constraint = await repo.get_by_id(constraint_id)
    return await _build_constraint_info(constraint, db)


async def delete_constraint(constraint_id: str, db: AsyncSession) -> bool:
    repo = ConstraintRepository(db)
    return await repo.delete(constraint_id)


async def get_constraints(
    school_id: str, semester_id: str, constraint_type: Optional[ConstraintType],
    page: int, page_size: int, db: AsyncSession
) -> PageResponse[ConstraintInfo]:
    repo = ConstraintRepository(db)
    if constraint_type:
        constraints, total = await repo.get_by_semester_and_type(
            school_id, semester_id, constraint_type, page, page_size
        )
    else:
        constraints, total = await repo.get_by_semester(
            school_id, semester_id, page, page_size
        )
    items = []
    for c in constraints:
        info = await _build_constraint_info(c, db)
        items.append(info)
    return PageResponse(items=items, total=total, page=page, page_size=page_size)


async def get_active_constraints(
    school_id: str, semester_id: str, db: AsyncSession
) -> List[ConstraintInfo]:
    repo = ConstraintRepository(db)
    constraints = await repo.get_active_constraints(school_id, semester_id)
    items = []
    for c in constraints:
        info = await _build_constraint_info(c, db)
        items.append(info)
    return items


async def toggle_constraint(constraint_id: str, db: AsyncSession) -> Optional[ConstraintInfo]:
    repo = ConstraintRepository(db)
    constraint = await repo.get_by_id(constraint_id)
    if constraint is None:
        return None
    await repo.update(constraint_id, {"is_active": not constraint.is_active})
    constraint = await repo.get_by_id(constraint_id)
    return await _build_constraint_info(constraint, db)


async def get_constraint_by_id(constraint_id: str, db: AsyncSession) -> Optional[ConstraintInfo]:
    repo = ConstraintRepository(db)
    constraint = await repo.get_by_id(constraint_id)
    if constraint is None:
        return None
    return await _build_constraint_info(constraint, db)
