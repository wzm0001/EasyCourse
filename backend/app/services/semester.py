from datetime import date
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.semester import Semester
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
        return None
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
