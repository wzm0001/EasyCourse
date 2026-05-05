from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User, UserRole, AccountStatus, School
from app.schemas.common import APIResponse, PageResponse
from app.schemas.user import SchoolInfo, SchoolUpdate, ApprovalAction
from app.repositories.user import SchoolRepository, UserRepository, ApprovalRepository
from app.services.user import approve_school, reject_school, request_data_change
from app.middleware.auth import require_super_admin, require_role, get_current_user_dependency

router = APIRouter(prefix="/schools", tags=["学校管理"])


@router.get("", response_model=APIResponse[PageResponse[SchoolInfo]])
async def get_schools(
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db),
):
    school_repo = SchoolRepository(db)
    schools, total = await school_repo.get_all(page=page, page_size=page_size)
    items = [
        SchoolInfo(
            id=s.id,
            name=s.name,
            code=s.code,
            address=s.address,
            contact_person=s.contact_person,
            contact_phone=s.contact_phone,
            status=s.status,
            created_at=s.created_at,
        )
        for s in schools
    ]
    return APIResponse.success(data=PageResponse(items=items, total=total, page=page, page_size=page_size))


@router.get("/pending", response_model=APIResponse[PageResponse[SchoolInfo]])
async def get_pending_schools(
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db),
):
    school_repo = SchoolRepository(db)
    from sqlalchemy import select, func
    count_result = await db.execute(
        select(func.count()).select_from(School).where(School.status == AccountStatus.PENDING)
    )
    total = count_result.scalar_one()
    offset = (page - 1) * page_size
    result = await db.execute(
        select(School).where(School.status == AccountStatus.PENDING).offset(offset).limit(page_size)
    )
    schools = list(result.scalars().all())
    items = [
        SchoolInfo(
            id=s.id,
            name=s.name,
            code=s.code,
            address=s.address,
            contact_person=s.contact_person,
            contact_phone=s.contact_phone,
            status=s.status,
            created_at=s.created_at,
        )
        for s in schools
    ]
    return APIResponse.success(data=PageResponse(items=items, total=total, page=page, page_size=page_size))


@router.get("/{school_id}", response_model=APIResponse[SchoolInfo])
async def get_school(
    school_id: str,
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    school_repo = SchoolRepository(db)
    school = await school_repo.get_by_id(school_id)
    if school is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="学校不存在")
    if current_user.role != UserRole.SUPER_ADMIN and current_user.school_id != school_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")
    info = SchoolInfo(
        id=school.id,
        name=school.name,
        code=school.code,
        address=school.address,
        contact_person=school.contact_person,
        contact_phone=school.contact_phone,
        status=school.status,
        created_at=school.created_at,
    )
    return APIResponse.success(data=info)


@router.put("/{school_id}", response_model=APIResponse)
async def update_school(
    school_id: str,
    request: SchoolUpdate,
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    school_repo = SchoolRepository(db)
    school = await school_repo.get_by_id(school_id)
    if school is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="学校不存在")
    if current_user.role == UserRole.SUPER_ADMIN:
        update_data = {k: v for k, v in request.model_dump().items() if v is not None}
        if update_data:
            await school_repo.update(school_id, update_data)
        return APIResponse.success(message="学校信息更新成功")
    elif current_user.role == UserRole.SCHOOL_ADMIN and current_user.school_id == school_id:
        change_data = {k: v for k, v in request.model_dump().items() if v is not None}
        if change_data:
            await request_data_change(school_id, change_data, current_user.id, db)
        return APIResponse.success(message="修改申请已提交，请等待审批")
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")


@router.post("/{school_id}/approve", response_model=APIResponse)
async def approve_school_endpoint(
    school_id: str,
    current_user: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db),
):
    school = await approve_school(school_id, current_user.id, db)
    if school is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="学校不存在")
    return APIResponse.success(message="学校已批准")


@router.post("/{school_id}/reject", response_model=APIResponse)
async def reject_school_endpoint(
    school_id: str,
    request: ApprovalAction,
    current_user: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db),
):
    school = await reject_school(school_id, current_user.id, request.reject_reason or "", db)
    if school is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="学校不存在")
    return APIResponse.success(message="学校已拒绝")
