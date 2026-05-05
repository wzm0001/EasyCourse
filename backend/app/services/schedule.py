import json
from typing import Optional, List
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.schedule import ScheduleCell, ScheduleLock
from app.models.basic_data import (
    TeachingArrangement, Class_, Course, Teacher, Classroom,
)
from app.models.period import DayPeriodConfig, GradePeriodConfig
from app.models.constraint import ScheduleConstraint, ConstraintType, ConstraintPriority
from app.repositories.schedule import (
    ScheduleCellRepository, ScheduleLockRepository, ScheduleConstraintRepository,
)
from app.repositories.basic_data import (
    TeachingArrangementRepository, ClassRepository, CourseRepository,
    TeacherRepository, ClassroomRepository,
)
from app.repositories.period import GradePeriodConfigRepository, DayPeriodConfigRepository
from app.schemas.schedule import (
    ScheduleCellInfo, ScheduleGrid, ConflictInfo, AutoScheduleResult,
    ScheduleLockInfo,
)


def _cell_to_info(cell: ScheduleCell, course_name: str = None, teacher_name: str = None, classroom_name: str = None) -> ScheduleCellInfo:
    return ScheduleCellInfo(
        id=cell.id,
        school_id=cell.school_id,
        semester_id=cell.semester_id,
        grade_id=cell.grade_id,
        class_id=cell.class_id,
        day_of_week=cell.day_of_week,
        period_type=cell.period_type,
        period_index=cell.period_index,
        course_id=cell.course_id,
        course_name=course_name,
        teacher_id=cell.teacher_id,
        teacher_name=teacher_name,
        classroom_id=cell.classroom_id,
        classroom_name=classroom_name,
        is_fixed=cell.is_fixed,
    )


async def check_teacher_conflict(teacher_id: str, day_of_week: int, period_type: str, period_index: int, semester_id: str, exclude_cell_id: Optional[str], db: AsyncSession) -> Optional[ScheduleCell]:
    if not teacher_id:
        return None
    repo = ScheduleCellRepository(db)
    result = await db.execute(
        select(ScheduleCell).where(
            ScheduleCell.teacher_id == teacher_id,
            ScheduleCell.day_of_week == day_of_week,
            ScheduleCell.period_type == period_type,
            ScheduleCell.period_index == period_index,
            ScheduleCell.semester_id == semester_id,
        )
    )
    cell = result.scalar_one_or_none()
    if cell is None:
        return None
    if exclude_cell_id and cell.id == exclude_cell_id:
        return None
    return cell


async def check_classroom_conflict(classroom_id: str, day_of_week: int, period_type: str, period_index: int, semester_id: str, exclude_cell_id: Optional[str], db: AsyncSession) -> Optional[ScheduleCell]:
    if not classroom_id:
        return None
    result = await db.execute(
        select(ScheduleCell).where(
            ScheduleCell.classroom_id == classroom_id,
            ScheduleCell.day_of_week == day_of_week,
            ScheduleCell.period_type == period_type,
            ScheduleCell.period_index == period_index,
            ScheduleCell.semester_id == semester_id,
        )
    )
    cell = result.scalar_one_or_none()
    if cell is None:
        return None
    if exclude_cell_id and cell.id == exclude_cell_id:
        return None
    return cell


async def check_class_conflict(class_id: str, day_of_week: int, period_type: str, period_index: int, semester_id: str, exclude_cell_id: Optional[str], db: AsyncSession) -> Optional[ScheduleCell]:
    result = await db.execute(
        select(ScheduleCell).where(
            ScheduleCell.class_id == class_id,
            ScheduleCell.day_of_week == day_of_week,
            ScheduleCell.period_type == period_type,
            ScheduleCell.period_index == period_index,
            ScheduleCell.semester_id == semester_id,
        )
    )
    cell = result.scalar_one_or_none()
    if cell is None:
        return None
    if exclude_cell_id and cell.id == exclude_cell_id:
        return None
    return cell


async def check_all_conflicts(cell_data: dict, semester_id: str, exclude_cell_id: Optional[str], db: AsyncSession) -> List[ConflictInfo]:
    conflicts = []
    teacher_id = cell_data.get("teacher_id")
    classroom_id = cell_data.get("classroom_id")
    class_id = cell_data.get("class_id")
    day_of_week = cell_data.get("day_of_week")
    period_type = cell_data.get("period_type")
    period_index = cell_data.get("period_index")

    if class_id:
        conflict = await check_class_conflict(class_id, day_of_week, period_type, period_index, semester_id, exclude_cell_id, db)
        if conflict:
            conflicts.append(ConflictInfo(
                type="class",
                cell_id=conflict.id,
                conflicting_with=conflict.course_id,
                message=f"班级在该时段已有课程安排",
            ))

    if teacher_id:
        conflict = await check_teacher_conflict(teacher_id, day_of_week, period_type, period_index, semester_id, exclude_cell_id, db)
        if conflict:
            conflicts.append(ConflictInfo(
                type="teacher",
                cell_id=conflict.id,
                conflicting_with=conflict.course_id,
                message=f"教师在该时段已有课程安排",
            ))

    if classroom_id:
        conflict = await check_classroom_conflict(classroom_id, day_of_week, period_type, period_index, semester_id, exclude_cell_id, db)
        if conflict:
            conflicts.append(ConflictInfo(
                type="classroom",
                cell_id=conflict.id,
                conflicting_with=conflict.course_id,
                message=f"教室在该时段已被占用",
            ))

    return conflicts


async def check_constraints(cell_data: dict, constraints: List[ScheduleConstraint], db: AsyncSession) -> List[ConflictInfo]:
    conflicts = []
    teacher_id = cell_data.get("teacher_id")
    classroom_id = cell_data.get("classroom_id")
    day_of_week = cell_data.get("day_of_week")
    period_type = cell_data.get("period_type")
    period_index = cell_data.get("period_index")

    for constraint in constraints:
        try:
            config = json.loads(constraint.config) if constraint.config else {}
        except (json.JSONDecodeError, TypeError):
            config = {}

        if constraint.constraint_type == ConstraintType.TEACHER_UNAVAILABLE:
            if constraint.target_type == "teacher" and constraint.target_id == teacher_id:
                unavailable_days = config.get("unavailable_days", [])
                unavailable_periods = config.get("unavailable_periods", [])
                if day_of_week in unavailable_days:
                    conflicts.append(ConflictInfo(
                        type="constraint",
                        message=f"教师不可用（约束：{constraint.constraint_type.value}）",
                    ))
                for p in unavailable_periods:
                    if p.get("day_of_week") == day_of_week and p.get("period_type") == period_type and p.get("period_index") == period_index:
                        conflicts.append(ConflictInfo(
                            type="constraint",
                            message=f"教师该时段不可用（约束：{constraint.constraint_type.value}）",
                        ))

        elif constraint.constraint_type == ConstraintType.CLASSROOM_UNAVAILABLE:
            if constraint.target_type == "classroom" and constraint.target_id == classroom_id:
                unavailable_days = config.get("unavailable_days", [])
                if day_of_week in unavailable_days:
                    conflicts.append(ConflictInfo(
                        type="constraint",
                        message=f"教室不可用（约束：{constraint.constraint_type.value}）",
                    ))

        elif constraint.constraint_type == ConstraintType.MAX_DAILY_PERIODS:
            if constraint.target_type == "teacher" and constraint.target_id == teacher_id:
                max_periods = config.get("max_periods", 6)
                result = await db.execute(
                    select(ScheduleCell).where(
                        ScheduleCell.teacher_id == teacher_id,
                        ScheduleCell.day_of_week == day_of_week,
                        ScheduleCell.semester_id == cell_data.get("semester_id", ""),
                    )
                )
                existing = list(result.scalars().all())
                if len(existing) >= max_periods:
                    conflicts.append(ConflictInfo(
                        type="constraint",
                        message=f"教师当日课时已达上限（约束：{constraint.constraint_type.value}）",
                    ))

    return conflicts


async def place_cell(data: dict, school_id: str, semester_id: str, db: AsyncSession) -> tuple[ScheduleCell, List[ConflictInfo]]:
    cell_repo = ScheduleCellRepository(db)
    class_repo = ClassRepository(db)

    cls = await class_repo.get_by_id(data["class_id"])
    if not cls:
        raise ValueError("班级不存在")

    grade_id = cls.grade_id

    existing = await cell_repo.get_cell(
        data["class_id"], data["day_of_week"],
        data["period_type"], data["period_index"], semester_id,
    )

    cell_data = {
        "school_id": school_id,
        "semester_id": semester_id,
        "grade_id": grade_id,
        "class_id": data["class_id"],
        "day_of_week": data["day_of_week"],
        "period_type": data["period_type"],
        "period_index": data["period_index"],
        "course_id": data.get("course_id"),
        "teacher_id": data.get("teacher_id"),
        "classroom_id": data.get("classroom_id"),
        "is_fixed": data.get("is_fixed", False),
    }

    conflicts = await check_all_conflicts(cell_data, semester_id, existing.id if existing else None, db)

    constraint_repo = ScheduleConstraintRepository(db)
    constraints = await constraint_repo.get_active_by_semester(school_id, semester_id)
    constraint_conflicts = await check_constraints(cell_data, constraints, db)
    conflicts.extend(constraint_conflicts)

    if existing:
        update_data = {k: v for k, v in cell_data.items() if k not in ("school_id", "semester_id", "grade_id", "class_id", "day_of_week", "period_type", "period_index")}
        updated = await cell_repo.update(existing.id, update_data)
        return updated, conflicts
    else:
        cell = ScheduleCell(**cell_data)
        created = await cell_repo.create(cell)
        return created, conflicts


async def remove_cell(cell_id: str, db: AsyncSession) -> bool:
    cell_repo = ScheduleCellRepository(db)
    cell = await cell_repo.get_by_id(cell_id)
    if not cell:
        return False
    if cell.is_fixed:
        raise ValueError("固定课程不可移除，请先取消固定")
    return await cell_repo.delete(cell_id)


async def fix_cell(cell_id: str, db: AsyncSession) -> Optional[ScheduleCell]:
    cell_repo = ScheduleCellRepository(db)
    return await cell_repo.update(cell_id, {"is_fixed": True})


async def unfix_cell(cell_id: str, db: AsyncSession) -> Optional[ScheduleCell]:
    cell_repo = ScheduleCellRepository(db)
    return await cell_repo.update(cell_id, {"is_fixed": False})


async def swap_cells(cell_id_1: str, cell_id_2: str, db: AsyncSession) -> tuple[bool, List[ConflictInfo]]:
    cell_repo = ScheduleCellRepository(db)
    cell1 = await cell_repo.get_by_id(cell_id_1)
    cell2 = await cell_repo.get_by_id(cell_id_2)
    if not cell1 or not cell2:
        raise ValueError("单元格不存在")

    conflicts = []

    temp1_data = {
        "school_id": cell1.school_id,
        "semester_id": cell1.semester_id,
        "grade_id": cell1.grade_id,
        "class_id": cell2.class_id,
        "day_of_week": cell2.day_of_week,
        "period_type": cell2.period_type,
        "period_index": cell2.period_index,
        "course_id": cell1.course_id,
        "teacher_id": cell1.teacher_id,
        "classroom_id": cell1.classroom_id,
        "is_fixed": cell1.is_fixed,
    }

    temp2_data = {
        "school_id": cell2.school_id,
        "semester_id": cell2.semester_id,
        "grade_id": cell2.grade_id,
        "class_id": cell1.class_id,
        "day_of_week": cell1.day_of_week,
        "period_type": cell1.period_type,
        "period_index": cell1.period_index,
        "course_id": cell2.course_id,
        "teacher_id": cell2.teacher_id,
        "classroom_id": cell2.classroom_id,
        "is_fixed": cell2.is_fixed,
    }

    conflicts1 = await check_all_conflicts(temp1_data, cell1.semester_id, cell_id_1, db)
    conflicts2 = await check_all_conflicts(temp2_data, cell2.semester_id, cell_id_2, db)
    conflicts.extend(conflicts1)
    conflicts.extend(conflicts2)

    await cell_repo.update(cell_id_1, {
        "class_id": cell2.class_id,
        "grade_id": cell2.grade_id,
        "day_of_week": cell2.day_of_week,
        "period_type": cell2.period_type,
        "period_index": cell2.period_index,
    })
    await cell_repo.update(cell_id_2, {
        "class_id": cell1.class_id,
        "grade_id": cell1.grade_id,
        "day_of_week": cell1.day_of_week,
        "period_type": cell1.period_type,
        "period_index": cell1.period_index,
    })

    return True, conflicts


async def auto_schedule(school_id: str, semester_id: str, grade_id: Optional[str], db: AsyncSession) -> AutoScheduleResult:
    cell_repo = ScheduleCellRepository(db)
    arrangement_repo = TeachingArrangementRepository(db)
    constraint_repo = ScheduleConstraintRepository(db)
    grade_period_repo = GradePeriodConfigRepository(db)
    day_period_repo = DayPeriodConfigRepository(db)
    class_repo = ClassRepository(db)

    result = await db.execute(
        select(TeachingArrangement).where(
            TeachingArrangement.school_id == school_id,
            TeachingArrangement.semester_id == semester_id,
        )
    )
    all_arrangements = list(result.scalars().all())

    if grade_id:
        classes_in_grade, _ = await class_repo.get_by_grade(grade_id)
        grade_class_ids = {c.id for c in classes_in_grade}
        arrangements = [a for a in all_arrangements if a.class_id in grade_class_ids]
    else:
        arrangements = all_arrangements

    constraints = await constraint_repo.get_active_by_semester(school_id, semester_id)

    fixed_cells = await cell_repo.get_fixed_cells(school_id, semester_id, grade_id)

    grade_ids = set()
    for arr in arrangements:
        cls = await class_repo.get_by_id(arr.class_id)
        if cls:
            grade_ids.add(cls.grade_id)
    if grade_id:
        grade_ids = {grade_id} if grade_id in grade_ids else grade_ids

    available_periods = {}
    for gid in grade_ids:
        grade_configs = await grade_period_repo.get_by_grade_semester(gid, semester_id)
        day_configs = await day_period_repo.get_by_grade_semester(gid, semester_id)
        unavailable_set = set()
        for dc in day_configs:
            if not dc.is_available:
                unavailable_set.add((dc.day_of_week, dc.period_type, dc.period_index))
        available_periods[gid] = []
        for gc in grade_configs:
            if (gc.day_of_week if hasattr(gc, 'day_of_week') else 0, gc.period_type, gc.period_index) not in unavailable_set:
                for day in range(1, 8):
                    key = (day, gc.period_type, gc.period_index)
                    is_unavailable = any(
                        dc.day_of_week == day and dc.period_type == gc.period_type and dc.period_index == gc.period_index and not dc.is_available
                        for dc in day_configs
                    )
                    if not is_unavailable:
                        available_periods[gid].append({
                            "day_of_week": day,
                            "period_type": gc.period_type.value if hasattr(gc.period_type, 'value') else gc.period_type,
                            "period_index": gc.period_index,
                        })

    priority_map = {
        ConstraintPriority.MANDATORY: 100,
        ConstraintPriority.HIGH: 75,
        ConstraintPriority.MEDIUM: 50,
        ConstraintPriority.LOW: 25,
    }

    def get_course_priority(course_id: str) -> int:
        priority = 50
        for c in constraints:
            if c.constraint_type == ConstraintType.FIXED_POSITION:
                try:
                    config = json.loads(c.config) if c.config else {}
                    if config.get("course_id") == course_id:
                        priority += priority_map.get(c.priority, 50)
                except (json.JSONDecodeError, TypeError):
                    pass
        return priority

    tasks = []
    for arr in arrangements:
        cls = await class_repo.get_by_id(arr.class_id)
        if not cls:
            continue
        for i in range(arr.weekly_hours):
            tasks.append({
                "teacher_id": arr.teacher_id,
                "course_id": arr.course_id,
                "class_id": arr.class_id,
                "grade_id": cls.grade_id,
                "priority": get_course_priority(arr.course_id),
            })

    tasks.sort(key=lambda t: t["priority"], reverse=True)

    results = AutoScheduleResult(total_tasks=len(tasks), scheduled=0, failed=0, conflicts=[])

    fixed_occupied = set()
    for fc in fixed_cells:
        fixed_occupied.add((fc.teacher_id, fc.day_of_week, fc.period_type, fc.period_index))
        fixed_occupied.add((fc.classroom_id, fc.day_of_week, fc.period_type, fc.period_index))
        fixed_occupied.add((fc.class_id, fc.day_of_week, fc.period_type, fc.period_index))

    for task in tasks:
        placed = False
        gid = task["grade_id"]
        periods = available_periods.get(gid, [])

        for period in periods:
            day = period["day_of_week"]
            pt = period["period_type"]
            pi = period["period_index"]

            cell_data = {
                "school_id": school_id,
                "semester_id": semester_id,
                "grade_id": gid,
                "class_id": task["class_id"],
                "day_of_week": day,
                "period_type": pt,
                "period_index": pi,
                "course_id": task["course_id"],
                "teacher_id": task["teacher_id"],
                "classroom_id": None,
                "is_fixed": False,
            }

            conflict = await check_class_conflict(task["class_id"], day, pt, pi, semester_id, None, db)
            if conflict:
                continue

            conflict = await check_teacher_conflict(task["teacher_id"], day, pt, pi, semester_id, None, db)
            if conflict:
                continue

            constraint_conflicts = await check_constraints(cell_data, constraints, db)
            mandatory_conflicts = [c for c in constraint_conflicts if "mandatory" in c.message.lower()]
            if mandatory_conflicts:
                continue

            cell = ScheduleCell(**cell_data)
            await cell_repo.create(cell)
            results.scheduled += 1
            placed = True
            break

        if not placed:
            results.failed += 1
            results.conflicts.append(ConflictInfo(
                type="auto_schedule",
                message=f"课程{task['course_id']}在班级{task['class_id']}无法找到无冲突时段",
            ))

    return results


async def acquire_lock(semester_id: str, school_id: str, user_id: str, db: AsyncSession) -> bool:
    lock_repo = ScheduleLockRepository(db)
    existing = await lock_repo.get_by_semester(semester_id)
    if existing:
        if existing.user_id != user_id:
            return False
        return True
    lock = ScheduleLock(
        school_id=school_id,
        semester_id=semester_id,
        user_id=user_id,
        locked_at=datetime.utcnow().isoformat(),
    )
    await lock_repo.create(lock)
    return True


async def release_lock(semester_id: str, user_id: str, db: AsyncSession) -> bool:
    lock_repo = ScheduleLockRepository(db)
    existing = await lock_repo.get_by_semester(semester_id)
    if not existing:
        return True
    if existing.user_id != user_id:
        return False
    await lock_repo.delete(existing.id)
    return True


async def check_lock(semester_id: str, db: AsyncSession) -> Optional[ScheduleLockInfo]:
    lock_repo = ScheduleLockRepository(db)
    existing = await lock_repo.get_by_semester(semester_id)
    if not existing:
        return None
    user_name = None
    from app.repositories.user import UserRepository
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(existing.user_id)
    if user:
        user_name = user.real_name
    return ScheduleLockInfo(
        id=existing.id,
        school_id=existing.school_id,
        semester_id=existing.semester_id,
        user_id=existing.user_id,
        user_name=user_name,
        locked_at=existing.locked_at,
    )


async def get_class_schedule(class_id: str, semester_id: str, db: AsyncSession) -> ScheduleGrid:
    cell_repo = ScheduleCellRepository(db)
    class_repo = ClassRepository(db)
    course_repo = CourseRepository(db)
    teacher_repo = TeacherRepository(db)
    classroom_repo = ClassroomRepository(db)

    cells = await cell_repo.get_by_class_semester(class_id, semester_id)
    cls = await class_repo.get_by_id(class_id)
    class_name = cls.name if cls else None

    cell_infos = []
    for cell in cells:
        course_name = None
        teacher_name = None
        classroom_name = None
        if cell.course_id:
            course = await course_repo.get_by_id(cell.course_id)
            course_name = course.name if course else None
        if cell.teacher_id:
            teacher = await teacher_repo.get_by_id(cell.teacher_id)
            teacher_name = teacher.name if teacher else None
        if cell.classroom_id:
            classroom = await classroom_repo.get_by_id(cell.classroom_id)
            classroom_name = classroom.name if classroom else None
        cell_infos.append(_cell_to_info(cell, course_name, teacher_name, classroom_name))

    return ScheduleGrid(class_id=class_id, class_name=class_name, cells=cell_infos)


async def get_teacher_schedule(teacher_id: str, semester_id: str, db: AsyncSession) -> ScheduleGrid:
    cell_repo = ScheduleCellRepository(db)
    course_repo = CourseRepository(db)
    teacher_repo = TeacherRepository(db)
    classroom_repo = ClassroomRepository(db)

    cells = await cell_repo.get_by_teacher_semester(teacher_id, semester_id)
    teacher = await teacher_repo.get_by_id(teacher_id)
    teacher_name = teacher.name if teacher else None

    cell_infos = []
    for cell in cells:
        course_name = None
        classroom_name = None
        if cell.course_id:
            course = await course_repo.get_by_id(cell.course_id)
            course_name = course.name if course else None
        if cell.classroom_id:
            classroom = await classroom_repo.get_by_id(cell.classroom_id)
            classroom_name = classroom.name if classroom else None
        cell_infos.append(_cell_to_info(cell, course_name, teacher_name, classroom_name))

    return ScheduleGrid(class_id=teacher_id, class_name=teacher_name, cells=cell_infos)


async def get_classroom_schedule(classroom_id: str, semester_id: str, db: AsyncSession) -> ScheduleGrid:
    cell_repo = ScheduleCellRepository(db)
    course_repo = CourseRepository(db)
    teacher_repo = TeacherRepository(db)
    classroom_repo = ClassroomRepository(db)

    cells = await cell_repo.get_by_classroom_semester(classroom_id, semester_id)
    classroom = await classroom_repo.get_by_id(classroom_id)
    classroom_name = classroom.name if classroom else None

    cell_infos = []
    for cell in cells:
        course_name = None
        teacher_name = None
        if cell.course_id:
            course = await course_repo.get_by_id(cell.course_id)
            course_name = course.name if course else None
        if cell.teacher_id:
            teacher = await teacher_repo.get_by_id(cell.teacher_id)
            teacher_name = teacher.name if teacher else None
        cell_infos.append(_cell_to_info(cell, course_name, teacher_name, classroom_name))

    return ScheduleGrid(class_id=classroom_id, class_name=classroom_name, cells=cell_infos)


async def get_grade_schedule(grade_id: str, semester_id: str, db: AsyncSession) -> List[ScheduleGrid]:
    class_repo = ClassRepository(db)
    classes, _ = await class_repo.get_by_grade(grade_id)
    grids = []
    for cls in classes:
        grid = await get_class_schedule(cls.id, semester_id, db)
        grids.append(grid)
    return grids


async def get_school_schedule(school_id: str, semester_id: str, db: AsyncSession) -> List[ScheduleGrid]:
    cell_repo = ScheduleCellRepository(db)
    class_repo = ClassRepository(db)

    classes, _ = await class_repo.get_by_semester(school_id, semester_id, page=1, page_size=10000)
    grids = []
    for cls in classes:
        grid = await get_class_schedule(cls.id, semester_id, db)
        grids.append(grid)
    return grids


async def clear_schedule(school_id: str, semester_id: str, grade_id: Optional[str], db: AsyncSession) -> int:
    cell_repo = ScheduleCellRepository(db)
    return await cell_repo.delete_by_semester(school_id, semester_id, grade_id)
