from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User, UserRole
from app.models.constraint import ConstraintType
from app.schemas.common import APIResponse, PageResponse
from app.schemas.constraint import ConstraintCreate, ConstraintUpdate, ConstraintInfo
from app.services.constraint import (
    create_constraint,
    update_constraint,
    delete_constraint,
    get_constraints,
    get_active_constraints,
    toggle_constraint,
    get_constraint_by_id,
)
from app.middleware.auth import get_current_user_dependency
from app.repositories.semester import SemesterRepository
from app.repositories.constraint import ConstraintRepository
from app.utils.semester_guard import check_semester_writable, resolve_semester_id_with_archive_check

router = APIRouter(prefix="/constraints", tags=["排课约束管理"])


async def _get_school_id(current_user: User) -> str:
    if current_user.role == UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="超级管理员需指定学校")
    if not current_user.school_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="当前用户未关联学校")
    return current_user.school_id


async def _resolve_semester_id(db: AsyncSession, school_id: str, semester_id: Optional[str], check_archive: bool = False) -> str:
    if check_archive:
        return await resolve_semester_id_with_archive_check(db, school_id, semester_id, raise_if_missing=True)
    if semester_id:
        return semester_id
    semester_repo = SemesterRepository(db)
    active = await semester_repo.get_active(school_id)
    if not active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="没有活跃学期，请指定学期")
    return active.id


@router.get("", response_model=APIResponse[PageResponse[ConstraintInfo]])
async def get_constraints_endpoint(
    semester_id: Optional[str] = Query(None),
    constraint_type: Optional[ConstraintType] = Query(None),
    page: int = Query(1),
    page_size: int = Query(20),
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    school_id = await _get_school_id(current_user)
    sid = await _resolve_semester_id(db, school_id, semester_id)
    result = await get_constraints(school_id, sid, constraint_type, page, page_size, db)
    return APIResponse.success(data=result)


@router.post("", response_model=APIResponse[ConstraintInfo])
async def create_constraint_endpoint(
    data: ConstraintCreate,
    semester_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    school_id = await _get_school_id(current_user)
    sid = await _resolve_semester_id(db, school_id, semester_id, check_archive=True)
    try:
        result = await create_constraint(data, school_id, sid, db)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return APIResponse.success(data=result)


@router.get("/active", response_model=APIResponse[list[ConstraintInfo]])
async def get_active_constraints_endpoint(
    semester_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    school_id = await _get_school_id(current_user)
    sid = await _resolve_semester_id(db, school_id, semester_id)
    result = await get_active_constraints(school_id, sid, db)
    return APIResponse.success(data=result)


@router.get("/{constraint_id}", response_model=APIResponse[ConstraintInfo])
async def get_constraint_detail_endpoint(
    constraint_id: str,
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    result = await get_constraint_by_id(constraint_id, db)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="约束不存在")
    if current_user.role != UserRole.SUPER_ADMIN and current_user.school_id != result.school_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")
    return APIResponse.success(data=result)


@router.put("/{constraint_id}", response_model=APIResponse[ConstraintInfo])
async def update_constraint_endpoint(
    constraint_id: str,
    data: ConstraintUpdate,
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    repo = ConstraintRepository(db)
    existing = await repo.get_by_id(constraint_id)
    if existing is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="约束不存在")
    if current_user.role != UserRole.SUPER_ADMIN and current_user.school_id != existing.school_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")
    await check_semester_writable(db, existing.semester_id)
    result = await update_constraint(constraint_id, data, db)
    return APIResponse.success(data=result)


@router.delete("/{constraint_id}", response_model=APIResponse)
async def delete_constraint_endpoint(
    constraint_id: str,
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    repo = ConstraintRepository(db)
    existing = await repo.get_by_id(constraint_id)
    if existing is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="约束不存在")
    if current_user.role != UserRole.SUPER_ADMIN and current_user.school_id != existing.school_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")
    await check_semester_writable(db, existing.semester_id)
    deleted = await delete_constraint(constraint_id, db)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="删除失败")
    return APIResponse.success(message="删除成功")


@router.post("/{constraint_id}/toggle", response_model=APIResponse[ConstraintInfo])
async def toggle_constraint_endpoint(
    constraint_id: str,
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    repo = ConstraintRepository(db)
    existing = await repo.get_by_id(constraint_id)
    if existing is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="约束不存在")
    if current_user.role != UserRole.SUPER_ADMIN and current_user.school_id != existing.school_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")
    await check_semester_writable(db, existing.semester_id)
    result = await toggle_constraint(constraint_id, db)
    return APIResponse.success(data=result)
