from datetime import date
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import delete as sa_delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.semester import Semester
from app.models.schedule import ScheduleCell, ScheduleLock
from app.models.basic_data import (
    Grade, Class_, GradeCourse, Teacher, TeacherCourse,
    Classroom, ClassroomCourse, TeachingArrangement,
)
from app.models.constraint import ScheduleConstraint
from app.repositories.semester import SemesterRepository


async def create_semester(data: dict, school_id: str, db: AsyncSession) -> Semester:
    repo = SemesterRepository(db)
    semester = Semester(
        school_id=school_id,
        name=data["name"],
        start_date=date.fromisoformat(data["start_date"]),
        end_date=date.fromisoformat(data["end_date"]),
        total_weeks=data.get("total_weeks", 20),
        description=data.get("description", ""),
        is_active=False,
        is_archived=False,
    )
    semester = await repo.create(semester)
    return semester


async def update_semester(semester_id: str, data: dict, db: AsyncSession) -> Optional[Semester]:
    repo = SemesterRepository(db)
    semester = await repo.get_by_id(semester_id)
    if semester is None:
        return None
    if semester.is_archived:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="该学期已归档，无法修改")
    update_data = {}
    for key, value in data.items():
        if value is None:
            continue
        if key in ("start_date", "end_date") and isinstance(value, str):
            update_data[key] = date.fromisoformat(value)
        else:
            update_data[key] = value
    if update_data:
        await repo.update(semester_id, update_data)
    return await repo.get_by_id(semester_id)


async def set_active_semester(semester_id: str, school_id: str, db: AsyncSession) -> Optional[Semester]:
    repo = SemesterRepository(db)
    semester = await repo.get_by_id(semester_id)
    if semester is None:
        return None
    if semester.school_id != school_id:
        return None
    if semester.is_archived:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="已归档的学期无法激活，请先取消归档")
    current_active = await repo.get_active(school_id)
    if current_active is not None:
        await repo.update(current_active.id, {"is_active": False})
    await repo.update(semester_id, {"is_active": True})
    return await repo.get_by_id(semester_id)


async def archive_semester(semester_id: str, db: AsyncSession) -> Optional[Semester]:
    repo = SemesterRepository(db)
    semester = await repo.get_by_id(semester_id)
    if semester is None:
        return None
    if semester.is_active:
        await repo.update(semester_id, {"is_active": False, "is_archived": True})
    else:
        await repo.update(semester_id, {"is_archived": True})
    return await repo.get_by_id(semester_id)


async def unarchive_semester(semester_id: str, db: AsyncSession) -> Optional[Semester]:
    repo = SemesterRepository(db)
    semester = await repo.get_by_id(semester_id)
    if semester is None:
        return None
    if not semester.is_archived:
        return semester
    await repo.update(semester_id, {"is_archived": False})
    return await repo.get_by_id(semester_id)


async def copy_semester_data(source_semester_id: str, target_semester_id: str, db: AsyncSession) -> Optional[Semester]:
    repo = SemesterRepository(db)
    source = await repo.get_by_id(source_semester_id)
    target = await repo.get_by_id(target_semester_id)
    if source is None or target is None:
        return None
    if source.school_id != target.school_id:
        return None
    return target


async def get_semesters(school_id: str, page: int, page_size: int, db: AsyncSession) -> tuple[list, int]:
    repo = SemesterRepository(db)
    return await repo.get_by_school(school_id, page=page, page_size=page_size)


async def delete_semester(semester_id: str, db: AsyncSession) -> bool:
    repo = SemesterRepository(db)
    semester = await repo.get_by_id(semester_id)
    if semester is None:
        return False
    if semester.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="无法删除当前激活的学期，请先激活其他学期")

    await db.execute(sa_delete(ScheduleCell).where(ScheduleCell.semester_id == semester_id))
    await db.execute(sa_delete(ScheduleLock).where(ScheduleLock.semester_id == semester_id))
    await db.execute(sa_delete(TeachingArrangement).where(TeachingArrangement.semester_id == semester_id))
    await db.execute(sa_delete(TeacherCourse).where(TeacherCourse.semester_id == semester_id))
    await db.execute(sa_delete(ClassroomCourse).where(ClassroomCourse.semester_id == semester_id))
    await db.execute(sa_delete(GradeCourse).where(GradeCourse.semester_id == semester_id))
    await db.execute(sa_delete(Class_).where(Class_.semester_id == semester_id))
    await db.execute(sa_delete(ScheduleConstraint).where(ScheduleConstraint.semester_id == semester_id))
    await db.execute(sa_delete(Teacher).where(Teacher.semester_id == semester_id))
    await db.execute(sa_delete(Classroom).where(Classroom.semester_id == semester_id))
    await db.execute(sa_delete(Grade).where(Grade.semester_id == semester_id))

    await db.execute(sa_delete(Semester).where(Semester.id == semester_id))
    await db.flush()
    return True
