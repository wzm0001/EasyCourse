from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User, UserRole
from app.schemas.common import APIResponse, PageResponse
from app.schemas.teaching_class import TeachingClassCreate, TeachingClassUpdate, TeachingClassInfo
from app.services import teaching_class as tc_service
from app.middleware.auth import get_current_user_dependency
from app.utils.semester_guard import check_semester_writable

router = APIRouter(prefix="/teaching-classes", tags=["走班教学班"])


async def _get_school_id(current_user: User) -> str:
    if current_user.role == UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="超级管理员需指定学校")
    if not current_user.school_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="当前用户未关联学校")
    return current_user.school_id


@router.get("", response_model=APIResponse[PageResponse[TeachingClassInfo]])
async def list_teaching_classes(
    semester_id: str = Query(...),
    grade_id: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    school_id = await _get_school_id(current_user)
    result = await tc_service.get_teaching_classes(school_id, semester_id, grade_id, page, page_size, db)
    return APIResponse.success(data=result)


@router.post("", response_model=APIResponse[TeachingClassInfo])
async def create_teaching_class(
    data: TeachingClassCreate,
    semester_id: str = Query(...),
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    school_id = await _get_school_id(current_user)
    await check_semester_writable(db, semester_id)
    result = await tc_service.create_teaching_class(data, school_id, semester_id, db)
    return APIResponse.success(data=result)


@router.get("/{id}", response_model=APIResponse[TeachingClassInfo])
async def get_teaching_class(
    id: str,
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    result = await tc_service.get_teaching_class(id, db)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="教学班不存在")
    return APIResponse.success(data=result)


@router.put("/{id}", response_model=APIResponse[TeachingClassInfo])
async def update_teaching_class(
    id: str,
    data: TeachingClassUpdate,
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    from app.repositories.teaching_class import TeachingClassRepository
    tc_repo = TeachingClassRepository(db)
    tc = await tc_repo.get_by_id(id)
    if not tc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="教学班不存在")
    await check_semester_writable(db, tc.semester_id)
    result = await tc_service.update_teaching_class(id, data, db)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="教学班不存在")
    return APIResponse.success(data=result)


@router.delete("/{id}", response_model=APIResponse)
async def delete_teaching_class(
    id: str,
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    from app.repositories.teaching_class import TeachingClassRepository
    tc_repo = TeachingClassRepository(db)
    tc = await tc_repo.get_by_id(id)
    if not tc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="教学班不存在")
    await check_semester_writable(db, tc.semester_id)
    deleted = await tc_service.delete_teaching_class(id, db)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="教学班不存在")
    return APIResponse.success(message="删除成功")
