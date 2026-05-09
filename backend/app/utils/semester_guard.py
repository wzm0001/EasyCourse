from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.semester import Semester
from app.repositories.semester import SemesterRepository


async def check_semester_writable(db: AsyncSession, semester_id: str) -> Semester:
    repo = SemesterRepository(db)
    semester = await repo.get_by_id(semester_id)
    if semester is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="学期不存在")
    if semester.is_archived:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="该学期已归档，无法修改数据")
    return semester


async def resolve_semester_id_with_archive_check(
    db: AsyncSession, school_id: str, semester_id: str | None, raise_if_missing: bool = True
) -> str | None:
    if semester_id:
        await check_semester_writable(db, semester_id)
        return semester_id
    repo = SemesterRepository(db)
    active = await repo.get_active(school_id)
    if not active:
        if raise_if_missing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="没有活跃学期，请指定学期")
        return None
    if active.is_archived:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="当前活跃学期已归档，无法修改数据")
    return active.id
