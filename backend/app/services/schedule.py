import json
import random
from typing import Optional, List
from datetime import datetime

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.schedule import ScheduleCell, ScheduleLock
from app.models.basic_data import (
    TeachingArrangement, Class_, Course, Teacher, Classroom, Grade, GradeCourse,
)
from app.models.period import DayPeriodConfig, GradePeriodConfig, PeriodType
from app.models.constraint import ScheduleConstraint, ConstraintType, ConstraintPriority
from app.repositories.schedule import (
    ScheduleCellRepository, ScheduleLockRepository, ScheduleConstraintRepository,
)
from app.repositories.basic_data import (
    TeachingArrangementRepository, ClassRepository, CourseRepository,
    TeacherRepository, ClassroomRepository, GradeRepository,
)
from app.repositories.period import GradePeriodConfigRepository, DayPeriodConfigRepository
from app.schemas.schedule import (
    ScheduleCellInfo, ScheduleGrid, ConflictInfo, AutoScheduleResult,
    ScheduleLockInfo, ConflictCheckRequest,
)


def _cell_to_info(cell: ScheduleCell, course_name: str = None, teacher_name: str = None, classroom_name: str = None, class_name: str = None, has_conflict: bool = False, conflict_reasons: list = None) -> ScheduleCellInfo:
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
        class_name=class_name,
        is_locked=cell.is_locked,
        has_conflict=has_conflict,
        conflict_reasons=conflict_reasons or [],
    )


async def check_teacher_conflict(teacher_id: str, day_of_week: int, period_type: str, period_index: int, semester_id: str, exclude_cell_id: Optional[str], db: AsyncSession) -> Optional[ScheduleCell]:
    if not teacher_id:
        return None
    result = await db.execute(
        select(ScheduleCell).where(
            ScheduleCell.teacher_id == teacher_id,
            ScheduleCell.day_of_week == day_of_week,
            ScheduleCell.period_type == period_type,
            ScheduleCell.period_index == period_index,
            ScheduleCell.semester_id == semester_id,
        )
    )
    cell = result.scalars().first()
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
    cell = result.scalars().first()
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
    cell = result.scalars().first()
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
                message="班级在该时段已有课程安排",
            ))

    if teacher_id:
        conflict = await check_teacher_conflict(teacher_id, day_of_week, period_type, period_index, semester_id, exclude_cell_id, db)
        if conflict:
            conflicts.append(ConflictInfo(
                type="teacher",
                cell_id=conflict.id,
                conflicting_with=conflict.course_id,
                message="教师在该时段已有课程安排",
            ))

    if classroom_id:
        conflict = await check_classroom_conflict(classroom_id, day_of_week, period_type, period_index, semester_id, exclude_cell_id, db)
        if conflict:
            conflicts.append(ConflictInfo(
                type="classroom",
                cell_id=conflict.id,
                conflicting_with=conflict.course_id,
                message="教室在该时段已被占用",
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


async def realtime_conflict_check(request: ConflictCheckRequest, semester_id: str, db: AsyncSession) -> List[ConflictInfo]:
    cell_data = {
        "teacher_id": request.teacher_id,
        "classroom_id": request.classroom_id,
        "class_id": request.class_id,
        "day_of_week": request.day_of_week,
        "period_type": request.period_type,
        "period_index": request.period_index,
        "semester_id": semester_id,
    }
    return await check_all_conflicts(cell_data, semester_id, request.exclude_cell_id, db)


async def place_cell(data: dict, school_id: str, semester_id: str, db: AsyncSession) -> tuple[ScheduleCell, List[ConflictInfo]]:
    cell_repo = ScheduleCellRepository(db)
    class_repo = ClassRepository(db)

    cls = await class_repo.get_by_id(data["class_id"])
    if not cls:
        raise ValueError("班级不存在")

    grade_id = cls.grade_id
    classroom_id = data.get("classroom_id")

    if not classroom_id and cls.classroom_id:
        classroom_id = cls.classroom_id

    existing = await cell_repo.get_cell(
        data["class_id"], data["day_of_week"],
        data["period_type"], data["period_index"], semester_id,
    )

    if existing and existing.is_locked:
        raise ValueError("该课程已锁定，请先取消锁定再修改")

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
        "classroom_id": classroom_id,
        "is_locked": data.get("is_locked", False),
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


async def drag_drop_place(data: dict, school_id: str, semester_id: str, db: AsyncSession) -> tuple[ScheduleCell, List[ConflictInfo]]:
    class_repo = ClassRepository(db)
    cls = await class_repo.get_by_id(data["target_class_id"])
    if not cls:
        raise ValueError("班级不存在")

    teacher_id = data["teacher_id"]
    course_id = data.get("course_id")

    if not course_id:
        tc_result = await db.execute(
            select(TeachingArrangement).where(
                TeachingArrangement.teacher_id == teacher_id,
                TeachingArrangement.class_id == data["target_class_id"],
                TeachingArrangement.semester_id == semester_id,
            )
        )
        arrangement = tc_result.scalars().first()
        if arrangement:
            course_id = arrangement.course_id

    place_data = {
        "class_id": data["target_class_id"],
        "day_of_week": data["target_day_of_week"],
        "period_type": data["target_period_type"],
        "period_index": data["target_period_index"],
        "teacher_id": teacher_id,
        "course_id": course_id,
        "classroom_id": cls.classroom_id,
    }

    return await place_cell(place_data, school_id, semester_id, db)


async def move_cell(cell_id: str, target_day_of_week: int, target_period_type: str, target_period_index: int, school_id: str, semester_id: str, db: AsyncSession) -> tuple[ScheduleCell, List[ConflictInfo]]:
    cell_repo = ScheduleCellRepository(db)
    cell = await cell_repo.get_by_id(cell_id)
    if not cell:
        raise ValueError("课程单元格不存在")
    if cell.is_locked:
        raise ValueError("锁定的课程不可移动，请先取消锁定")

    existing_at_target = await cell_repo.get_cell(
        cell.class_id, target_day_of_week,
        target_period_type, target_period_index, semester_id,
    )
    if existing_at_target and existing_at_target.is_locked:
        raise ValueError("目标位置已有锁定课程，不可覆盖")

    if existing_at_target and existing_at_target.id != cell_id:
        await cell_repo.delete(existing_at_target.id)

    cell_data = {
        "school_id": cell.school_id,
        "semester_id": cell.semester_id,
        "grade_id": cell.grade_id,
        "class_id": cell.class_id,
        "day_of_week": target_day_of_week,
        "period_type": target_period_type,
        "period_index": target_period_index,
        "course_id": cell.course_id,
        "teacher_id": cell.teacher_id,
        "classroom_id": cell.classroom_id,
        "is_locked": cell.is_locked,
    }

    conflicts = await check_all_conflicts(cell_data, semester_id, cell_id, db)

    constraint_repo = ScheduleConstraintRepository(db)
    constraints = await constraint_repo.get_active_by_semester(school_id, semester_id)
    constraint_conflicts = await check_constraints(cell_data, constraints, db)
    conflicts.extend(constraint_conflicts)

    updated = await cell_repo.update(cell_id, {
        "day_of_week": target_day_of_week,
        "period_type": target_period_type,
        "period_index": target_period_index,
    })
    return updated, conflicts


async def remove_cell(cell_id: str, db: AsyncSession) -> bool:
    cell_repo = ScheduleCellRepository(db)
    cell = await cell_repo.get_by_id(cell_id)
    if not cell:
        return False
    if cell.is_locked:
        raise ValueError("锁定课程不可移除，请先取消锁定")
    return await cell_repo.delete(cell_id)


async def lock_cell(cell_id: str, db: AsyncSession) -> Optional[ScheduleCell]:
    cell_repo = ScheduleCellRepository(db)
    cell = await cell_repo.get_by_id(cell_id)
    if not cell:
        return None
    if not cell.course_id:
        raise ValueError("空单元格无法锁定")
    return await cell_repo.update(cell_id, {"is_locked": True})


async def unlock_cell(cell_id: str, db: AsyncSession) -> Optional[ScheduleCell]:
    cell_repo = ScheduleCellRepository(db)
    return await cell_repo.update(cell_id, {"is_locked": False})


async def swap_cells(cell_id_1: str, cell_id_2: str, db: AsyncSession) -> tuple[bool, List[ConflictInfo]]:
    cell_repo = ScheduleCellRepository(db)
    cell1 = await cell_repo.get_by_id(cell_id_1)
    cell2 = await cell_repo.get_by_id(cell_id_2)
    if not cell1 or not cell2:
        raise ValueError("单元格不存在")

    if cell1.is_locked or cell2.is_locked:
        raise ValueError("锁定的课程不可交换，请先取消锁定")

    conflicts = []

    cell1_course_id = cell1.course_id
    cell1_teacher_id = cell1.teacher_id
    cell1_classroom_id = cell1.classroom_id
    cell2_course_id = cell2.course_id
    cell2_teacher_id = cell2.teacher_id
    cell2_classroom_id = cell2.classroom_id

    swapped1_data = {
        "school_id": cell1.school_id,
        "semester_id": cell1.semester_id,
        "grade_id": cell1.grade_id,
        "class_id": cell1.class_id,
        "day_of_week": cell1.day_of_week,
        "period_type": cell1.period_type,
        "period_index": cell1.period_index,
        "course_id": cell2_course_id,
        "teacher_id": cell2_teacher_id,
        "classroom_id": cell2_classroom_id,
    }

    swapped2_data = {
        "school_id": cell2.school_id,
        "semester_id": cell2.semester_id,
        "grade_id": cell2.grade_id,
        "class_id": cell2.class_id,
        "day_of_week": cell2.day_of_week,
        "period_type": cell2.period_type,
        "period_index": cell2.period_index,
        "course_id": cell1_course_id,
        "teacher_id": cell1_teacher_id,
        "classroom_id": cell1_classroom_id,
    }

    conflicts1 = await check_all_conflicts(swapped1_data, cell1.semester_id, cell_id_1, db)
    conflicts2 = await check_all_conflicts(swapped2_data, cell2.semester_id, cell_id_2, db)
    conflicts.extend(conflicts1)
    conflicts.extend(conflicts2)

    await cell_repo.update(cell_id_1, {
        "course_id": cell2_course_id,
        "teacher_id": cell2_teacher_id,
        "classroom_id": cell2_classroom_id,
    })
    await cell_repo.update(cell_id_2, {
        "course_id": cell1_course_id,
        "teacher_id": cell1_teacher_id,
        "classroom_id": cell1_classroom_id,
    })

    return True, conflicts


async def _clear_old_schedule(
    school_id: str,
    semester_id: str,
    grade_id: Optional[str],
    keep_locked: bool,
    db: AsyncSession,
) -> List[ScheduleCell]:
    if keep_locked:
        conditions = [
            ScheduleCell.school_id == school_id,
            ScheduleCell.semester_id == semester_id,
            ScheduleCell.is_locked == False,
        ]
        if grade_id:
            conditions.append(ScheduleCell.grade_id == grade_id)
        await db.execute(delete(ScheduleCell).where(*conditions))
        locked_conditions = [
            ScheduleCell.school_id == school_id,
            ScheduleCell.semester_id == semester_id,
            ScheduleCell.is_locked == True,
        ]
        if grade_id:
            locked_conditions.append(ScheduleCell.grade_id == grade_id)
        locked_result = await db.execute(select(ScheduleCell).where(*locked_conditions))
        locked_cells = list(locked_result.scalars().all())
    else:
        conditions = [
            ScheduleCell.school_id == school_id,
            ScheduleCell.semester_id == semester_id,
        ]
        if grade_id:
            conditions.append(ScheduleCell.grade_id == grade_id)
        await db.execute(delete(ScheduleCell).where(*conditions))
        locked_cells = []
    await db.flush()
    return locked_cells


async def _get_teaching_arrangements(
    school_id: str,
    semester_id: str,
    grade_id: Optional[str],
    db: AsyncSession,
) -> List[TeachingArrangement]:
    class_repo = ClassRepository(db)

    result_query = await db.execute(
        select(TeachingArrangement).where(
            TeachingArrangement.school_id == school_id,
            TeachingArrangement.semester_id == semester_id,
        )
    )
    all_arrangements = list(result_query.scalars().all())

    if grade_id:
        classes_in_grade, _ = await class_repo.get_by_grade(grade_id)
        grade_class_ids = {c.id for c in classes_in_grade}
        arrangements = [a for a in all_arrangements if a.class_id in grade_class_ids]
    else:
        arrangements = all_arrangements

    return arrangements


async def _build_available_periods(
    grade_ids: set,
    semester_id: str,
    db: AsyncSession,
) -> dict:
    grade_repo = GradeRepository(db)
    available_periods = {}

    for gid in grade_ids:
        grade_obj = await grade_repo.get_by_id(gid)
        mr_count = grade_obj.morning_reading_count if grade_obj else 1
        rc_count = grade_obj.regular_class_count if grade_obj else 8
        es_count = grade_obj.evening_study_count if grade_obj else 0

        day_result = await db.execute(
            select(DayPeriodConfig).where(
                DayPeriodConfig.grade_id == gid,
                DayPeriodConfig.semester_id == semester_id,
            )
        )
        day_configs = list(day_result.scalars().all())
        unavailable_set = set()
        for dc in day_configs:
            if not dc.is_available:
                period_type_value = dc.period_type.value if hasattr(dc.period_type, 'value') else dc.period_type
                unavailable_set.add((dc.day_of_week, period_type_value, dc.period_index))

        available_periods[gid] = []
        for day in range(1, 8):
            for idx in range(1, mr_count + 1):
                if (day, "morning_reading", idx) not in unavailable_set:
                    available_periods[gid].append({
                        "day_of_week": day,
                        "period_type": "morning_reading",
                        "period_index": idx,
                    })
            for idx in range(1, rc_count + 1):
                if (day, "regular", idx) not in unavailable_set:
                    available_periods[gid].append({
                        "day_of_week": day,
                        "period_type": "regular",
                        "period_index": idx,
                    })
            for idx in range(1, es_count + 1):
                if (day, "evening_study", idx) not in unavailable_set:
                    available_periods[gid].append({
                        "day_of_week": day,
                        "period_type": "evening_study",
                        "period_index": idx,
                    })

    return available_periods


async def _generate_schedule_tasks(
    arrangements: List[TeachingArrangement],
    db: AsyncSession,
) -> List[dict]:
    class_repo = ClassRepository(db)
    tasks = []

    for arr in arrangements:
        cls = await class_repo.get_by_id(arr.class_id)
        if not cls:
            continue
        gc_result = await db.execute(
            select(GradeCourse).where(
                GradeCourse.grade_id == cls.grade_id,
                GradeCourse.course_id == arr.course_id,
            )
        )
        grade_courses = list(gc_result.scalars().all())
        if grade_courses:
            for gc in grade_courses:
                gc_hours = gc.weekly_hours if gc.weekly_hours else 1
                for i in range(gc_hours):
                    tasks.append({
                        "teacher_id": arr.teacher_id,
                        "course_id": arr.course_id,
                        "class_id": arr.class_id,
                        "grade_id": cls.grade_id,
                        "classroom_id": cls.classroom_id,
                        "period_type": gc.period_type.value if gc.period_type else "regular",
                    })
        else:
            for i in range(arr.weekly_hours):
                tasks.append({
                    "teacher_id": arr.teacher_id,
                    "course_id": arr.course_id,
                    "class_id": arr.class_id,
                    "grade_id": cls.grade_id,
                    "classroom_id": cls.classroom_id,
                    "period_type": "regular",
                })

    random.shuffle(tasks)
    return tasks


async def _execute_scheduling(
    tasks: List[dict],
    available_periods: dict,
    locked_cells: List[ScheduleCell],
    constraints: List,
    school_id: str,
    semester_id: str,
    db: AsyncSession,
) -> AutoScheduleResult:
    cell_repo = ScheduleCellRepository(db)

    locked_occupied = set()
    for lc in locked_cells:
        if lc.teacher_id:
            locked_occupied.add((lc.teacher_id, lc.day_of_week, lc.period_type, lc.period_index))
        if lc.classroom_id:
            locked_occupied.add((lc.classroom_id, lc.day_of_week, lc.period_type, lc.period_index))
        locked_occupied.add((lc.class_id, lc.day_of_week, lc.period_type, lc.period_index))

    occupied_slots = set(locked_occupied)

    results = AutoScheduleResult(total_tasks=len(tasks), scheduled=0, failed=0, conflicts=[])

    for task in tasks:
        placed = False
        gid = task["grade_id"]
        periods = available_periods.get(gid, [])

        for period in periods:
            day = period["day_of_week"]
            pt = period["period_type"]
            pi = period["period_index"]

            if pt != task["period_type"]:
                continue

            slot_key_class = (task["class_id"], day, pt, pi)
            if slot_key_class in occupied_slots:
                continue

            slot_key_teacher = (task["teacher_id"], day, pt, pi)
            if task["teacher_id"] and slot_key_teacher in occupied_slots:
                continue

            if task["classroom_id"]:
                slot_key_classroom = (task["classroom_id"], day, pt, pi)
                if slot_key_classroom in occupied_slots:
                    continue

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
                "classroom_id": task["classroom_id"],
                "is_locked": False,
            }

            constraint_conflicts = await check_constraints(cell_data, constraints, db)
            mandatory_conflicts = [c for c in constraint_conflicts if "mandatory" in c.message.lower()]
            if mandatory_conflicts:
                continue

            cell = ScheduleCell(**cell_data)
            await cell_repo.create(cell)

            occupied_slots.add(slot_key_class)
            if task["teacher_id"]:
                occupied_slots.add(slot_key_teacher)
            if task["classroom_id"]:
                occupied_slots.add(slot_key_classroom)

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


async def auto_schedule(school_id: str, semester_id: str, grade_id: Optional[str], keep_locked: bool, db: AsyncSession) -> AutoScheduleResult:
    locked_cells = await _clear_old_schedule(school_id, semester_id, grade_id, keep_locked, db)

    arrangements = await _get_teaching_arrangements(school_id, semester_id, grade_id, db)

    constraint_repo = ScheduleConstraintRepository(db)
    constraints = await constraint_repo.get_active_by_semester(school_id, semester_id)

    class_repo = ClassRepository(db)
    grade_ids = set()
    for arr in arrangements:
        cls = await class_repo.get_by_id(arr.class_id)
        if cls:
            grade_ids.add(cls.grade_id)
    if grade_id:
        grade_ids = {grade_id} if grade_id in grade_ids else grade_ids

    available_periods = await _build_available_periods(grade_ids, semester_id, db)

    tasks = await _generate_schedule_tasks(arrangements, db)

    results = await _execute_scheduling(
        tasks, available_periods, locked_cells, constraints,
        school_id, semester_id, db,
    )

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

    cell_lookup: dict[str, ScheduleCell] = {c.id: c for c in cells}
    cell_conflicts: dict[str, list[str]] = {c.id: [] for c in cells}
    all_conflicts: list[ConflictInfo] = []

    for cell in cells:
        cell_data = {
            "class_id": cell.class_id,
            "day_of_week": cell.day_of_week,
            "period_type": cell.period_type,
            "period_index": cell.period_index,
            "teacher_id": cell.teacher_id,
            "classroom_id": cell.classroom_id,
        }
        cf = await check_all_conflicts(cell_data, semester_id, cell.id, db)
        if cf:
            enriched = []
            for c in cf:
                enriched.append(ConflictInfo(
                    type=c.type,
                    cell_id=c.cell_id,
                    conflicting_with=c.conflicting_with,
                    message=f"{cell.class_id}_{cell.day_of_week}_{cell.period_type}_{cell.period_index} | {c.message}",
                ))
            cf = enriched
            cell_conflicts[cell.id].extend([c.message for c in enriched])
        all_conflicts.extend(cf)

    deduped: list[ConflictInfo] = []
    seen = set()
    for c in all_conflicts:
        key = c.type + c.message
        if key not in seen:
            seen.add(key)
            deduped.append(c)
    all_conflicts = deduped

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
            classroom_name = f"{classroom.building_name} {classroom.room_number}" if classroom else None

        has_cf = len(cell_conflicts.get(cell.id, [])) > 0
        reasons = cell_conflicts.get(cell.id, [])
        cell_infos.append(_cell_to_info(cell, course_name, teacher_name, classroom_name, class_name, has_cf, reasons))

    return ScheduleGrid(class_id=class_id, class_name=class_name, cells=cell_infos, conflicts=all_conflicts)


async def get_teacher_schedule(teacher_id: str, semester_id: str, db: AsyncSession) -> ScheduleGrid:
    cell_repo = ScheduleCellRepository(db)
    course_repo = CourseRepository(db)
    teacher_repo = TeacherRepository(db)
    classroom_repo = ClassroomRepository(db)
    class_repo = ClassRepository(db)

    cells = await cell_repo.get_by_teacher_semester(teacher_id, semester_id)
    teacher = await teacher_repo.get_by_id(teacher_id)
    teacher_name = teacher.name if teacher else None

    cell_infos = []
    for cell in cells:
        course_name = None
        classroom_name = None
        cn = None
        if cell.course_id:
            course = await course_repo.get_by_id(cell.course_id)
            course_name = course.name if course else None
        if cell.classroom_id:
            classroom = await classroom_repo.get_by_id(cell.classroom_id)
            classroom_name = f"{classroom.building_name} {classroom.room_number}" if classroom else None
        if cell.class_id:
            cls = await class_repo.get_by_id(cell.class_id)
            cn = cls.name if cls else None
        cell_infos.append(_cell_to_info(cell, course_name, teacher_name, classroom_name, cn))

    return ScheduleGrid(class_id=teacher_id, class_name=teacher_name, cells=cell_infos)


async def get_classroom_schedule(classroom_id: str, semester_id: str, db: AsyncSession) -> ScheduleGrid:
    cell_repo = ScheduleCellRepository(db)
    course_repo = CourseRepository(db)
    teacher_repo = TeacherRepository(db)
    classroom_repo = ClassroomRepository(db)
    class_repo = ClassRepository(db)

    cells = await cell_repo.get_by_classroom_semester(classroom_id, semester_id)
    classroom = await classroom_repo.get_by_id(classroom_id)
    classroom_name = f"{classroom.building_name} {classroom.room_number}" if classroom else None

    cell_infos = []
    for cell in cells:
        course_name = None
        teacher_name = None
        cn = None
        if cell.course_id:
            course = await course_repo.get_by_id(cell.course_id)
            course_name = course.name if course else None
        if cell.teacher_id:
            teacher = await teacher_repo.get_by_id(cell.teacher_id)
            teacher_name = teacher.name if teacher else None
        if cell.class_id:
            cls = await class_repo.get_by_id(cell.class_id)
            cn = cls.name if cls else None
        cell_infos.append(_cell_to_info(cell, course_name, teacher_name, classroom_name, cn))

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
    class_repo = ClassRepository(db)
    classes, _ = await class_repo.get_by_semester(school_id, semester_id, page=1, page_size=10000)
    grids = []
    for cls in classes:
        grid = await get_class_schedule(cls.id, semester_id, db)
        grids.append(grid)
    return grids


async def clear_schedule(school_id: str, semester_id: str, grade_id: Optional[str], keep_locked: bool, db: AsyncSession) -> int:
    cell_repo = ScheduleCellRepository(db)
    if keep_locked:
        query = delete(ScheduleCell).where(
            ScheduleCell.school_id == school_id,
            ScheduleCell.semester_id == semester_id,
            ScheduleCell.is_locked == False,
        )
        if grade_id:
            query = query.where(ScheduleCell.grade_id == grade_id)
        result = await db.execute(query)
        await db.flush()
        return result.rowcount
    else:
        return await cell_repo.delete_by_semester(school_id, semester_id, grade_id)
