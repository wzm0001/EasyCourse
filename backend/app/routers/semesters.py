from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User, UserRole
from app.schemas.common import APIResponse, PageResponse
from app.schemas.semester import SemesterCreate, SemesterUpdate, SemesterInfo, SemesterCopyRequest
from app.repositories.semester import SemesterRepository
from app.services.semester import (
    create_semester,
    update_semester,
    set_active_semester,
    archive_semester,
    copy_semester_data,
    get_semesters,
)
from app.middleware.auth import get_current_user_dependency
from app.middleware.tenant import get_tenant_filter

router = APIRouter(prefix="/semesters", tags=["学期管理"])


@router.get("/active", response_model=APIResponse[SemesterInfo])
async def get_active_semester(
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    tenant = get_tenant_filter(current_user)
    if tenant.school_id is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")
    repo = SemesterRepository(db)
    active = await repo.get_active(tenant.school_id)
    if not active:
        return APIResponse.success(data=None)
    return APIResponse.success(data=SemesterInfo.from_orm(active))


@router.get("", response_model=APIResponse[PageResponse[SemesterInfo]])
async def list_semesters(
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    tenant = get_tenant_filter(current_user)
    if tenant.school_id is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")
    semesters, total = await get_semesters(tenant.school_id, page, page_size, db)
    items = [SemesterInfo.from_orm(s) for s in semesters]
    return APIResponse.success(data=PageResponse(items=items, total=total, page=page, page_size=page_size))


@router.post("", response_model=APIResponse[SemesterInfo])
async def create_semester_endpoint(
    request: SemesterCreate,
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    tenant = get_tenant_filter(current_user)
    if tenant.school_id is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")
    if current_user.role not in (UserRole.SUPER_ADMIN, UserRole.SCHOOL_ADMIN):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")
    semester = await create_semester(request.model_dump(), tenant.school_id, db)
    return APIResponse.success(data=SemesterInfo.from_orm(semester))


@router.get("/{semester_id}", response_model=APIResponse[SemesterInfo])
async def get_semester(
    semester_id: str,
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    repo = SemesterRepository(db)
    semester = await repo.get_by_id(semester_id)
    if semester is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="学期不存在")
    tenant = get_tenant_filter(current_user)
    if tenant.school_id is not None and semester.school_id != tenant.school_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")
    return APIResponse.success(data=SemesterInfo.from_orm(semester))


@router.put("/{semester_id}", response_model=APIResponse[SemesterInfo])
async def update_semester_endpoint(
    semester_id: str,
    request: SemesterUpdate,
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    if current_user.role not in (UserRole.SUPER_ADMIN, UserRole.SCHOOL_ADMIN):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")
    repo = SemesterRepository(db)
    semester = await repo.get_by_id(semester_id)
    if semester is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="学期不存在")
    tenant = get_tenant_filter(current_user)
    if tenant.school_id is not None and semester.school_id != tenant.school_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")
    update_data = {k: v for k, v in request.model_dump().items() if v is not None}
    updated = await update_semester(semester_id, update_data, db)
    return APIResponse.success(data=SemesterInfo.from_orm(updated))


@router.post("/{semester_id}/activate", response_model=APIResponse[SemesterInfo])
async def activate_semester(
    semester_id: str,
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    if current_user.role not in (UserRole.SUPER_ADMIN, UserRole.SCHOOL_ADMIN):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")
    tenant = get_tenant_filter(current_user)
    if tenant.school_id is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")
    semester = await set_active_semester(semester_id, tenant.school_id, db)
    if semester is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="学期不存在或无法激活")
    return APIResponse.success(data=SemesterInfo.from_orm(semester))


@router.post("/{semester_id}/archive", response_model=APIResponse[SemesterInfo])
async def archive_semester_endpoint(
    semester_id: str,
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    if current_user.role not in (UserRole.SUPER_ADMIN, UserRole.SCHOOL_ADMIN):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")
    semester = await archive_semester(semester_id, db)
    if semester is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="学期不存在")
    tenant = get_tenant_filter(current_user)
    if tenant.school_id is not None and semester.school_id != tenant.school_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")
    return APIResponse.success(data=SemesterInfo.from_orm(semester))


@router.post("/{semester_id}/copy", response_model=APIResponse[SemesterInfo])
async def copy_semester_endpoint(
    semester_id: str,
    request: SemesterCopyRequest,
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    if current_user.role not in (UserRole.SUPER_ADMIN, UserRole.SCHOOL_ADMIN):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")
    tenant = get_tenant_filter(current_user)
    if tenant.school_id is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")
    repo = SemesterRepository(db)
    source = await repo.get_by_id(semester_id)
    if source is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="源学期不存在")
    if tenant.school_id is not None and source.school_id != tenant.school_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")
    target = await copy_semester_data(semester_id, request.target_semester_id, db)
    if target is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="目标学期不存在或不在同一学校")
    return APIResponse.success(data=SemesterInfo.from_orm(target))
