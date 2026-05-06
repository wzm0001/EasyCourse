import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import List

from app.database import get_db
from app.models.user import User, UserRole, AccountStatus, School
from app.schemas.common import APIResponse, PageResponse
from app.schemas.user import SchoolInfo, SchoolUpdate, ApprovalAction, SchoolDetailInfo
from app.repositories.user import SchoolRepository, UserRepository, ApprovalRepository
from app.services.user import approve_school, reject_school, request_data_change
from app.services.auth import get_password_hash
from app.middleware.auth import require_super_admin, require_role, get_current_user_dependency
from app.config import settings

router = APIRouter(prefix="/schools", tags=["学校管理"])

DEFAULT_PASSWORD = "Admin@123"


class ResetPasswordBody(BaseModel):
    new_password: str = DEFAULT_PASSWORD


class BatchResetPasswordRequest(BaseModel):
    school_ids: List[str]
    new_password: str = DEFAULT_PASSWORD


async def _get_school_admin_info(school_id: str, user_repo: UserRepository, db: AsyncSession) -> dict:
    from sqlalchemy import select
    result = await db.execute(
        select(User).where(User.school_id == school_id, User.role == UserRole.SCHOOL_ADMIN)
    )
    admin = result.scalar_one_or_none()
    if admin is None:
        return {}
    return {
        "admin_username": admin.username,
        "admin_real_name": admin.real_name,
        "admin_phone": admin.phone,
        "admin_is_active": admin.is_active,
        "admin_email": admin.email,
    }


async def _get_school_user_count(school_id: str, db: AsyncSession) -> int:
    from sqlalchemy import select, func
    result = await db.execute(
        select(func.count()).select_from(User).where(User.school_id == school_id)
    )
    return result.scalar_one()


async def _build_school_detail(s: School, user_repo: UserRepository, db: AsyncSession) -> SchoolDetailInfo:
    admin_info = await _get_school_admin_info(s.id, user_repo, db)
    user_count = await _get_school_user_count(s.id, db)
    return SchoolDetailInfo(
        id=s.id,
        name=s.name,
        code=s.code,
        address=s.address,
        contact_person=s.contact_person,
        contact_phone=s.contact_phone,
        status=s.status,
        created_at=s.created_at,
        school_type=s.school_type,
        province=s.province,
        city=s.city,
        district=s.district,
        attachment=s.attachment,
        admin_username=admin_info.get("admin_username", ""),
        admin_real_name=admin_info.get("admin_real_name", ""),
        admin_phone=admin_info.get("admin_phone", ""),
        admin_is_active=admin_info.get("admin_is_active", True),
        admin_email=admin_info.get("admin_email", ""),
        user_count=user_count,
    )


@router.post("/upload", response_model=APIResponse)
async def upload_file(
    file: UploadFile = File(...),
):
    upload_dir = settings.UPLOAD_DIR
    os.makedirs(upload_dir, exist_ok=True)
    ext = os.path.splitext(file.filename or "")[1]
    if ext.lower() not in (".pdf", ".jpg", ".jpeg", ".png", ".doc", ".docx"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="不支持的文件类型")
    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(upload_dir, filename)
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="文件大小不能超过10MB")
    with open(filepath, "wb") as f:
        f.write(content)
    url = f"/api/v1/schools/files/{filename}"
    return APIResponse.success(data={"url": url, "filename": file.filename})


@router.get("/files/{filename}")
async def get_uploaded_file(filename: str):
    from fastapi.responses import FileResponse
    filepath = os.path.join(settings.UPLOAD_DIR, filename)
    if not os.path.exists(filepath) or not os.path.abspath(filepath).startswith(os.path.abspath(settings.UPLOAD_DIR)):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文件不存在")
    return FileResponse(filepath)


@router.get("", response_model=APIResponse[PageResponse[SchoolDetailInfo]])
async def get_schools(
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db),
):
    school_repo = SchoolRepository(db)
    user_repo = UserRepository(db)
    schools, total = await school_repo.get_all(page=page, page_size=page_size)
    items = [await _build_school_detail(s, user_repo, db) for s in schools]
    return APIResponse.success(data=PageResponse(items=items, total=total, page=page, page_size=page_size))


@router.get("/pending", response_model=APIResponse[PageResponse[SchoolDetailInfo]])
async def get_pending_schools(
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db),
):
    school_repo = SchoolRepository(db)
    user_repo = UserRepository(db)
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
    items = [await _build_school_detail(s, user_repo, db) for s in schools]
    return APIResponse.success(data=PageResponse(items=items, total=total, page=page, page_size=page_size))


@router.get("/{school_id}", response_model=APIResponse[SchoolDetailInfo])
async def get_school(
    school_id: str,
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    school_repo = SchoolRepository(db)
    user_repo = UserRepository(db)
    school = await school_repo.get_by_id(school_id)
    if school is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="学校不存在")
    if current_user.role != UserRole.SUPER_ADMIN and current_user.school_id != school_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")
    info = await _build_school_detail(school, user_repo, db)
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


@router.post("/{school_id}/reset-password", response_model=APIResponse)
async def reset_school_admin_password(
    school_id: str,
    request: ResetPasswordBody = ResetPasswordBody(),
    current_user: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db),
):
    from sqlalchemy import select
    result = await db.execute(
        select(User).where(User.school_id == school_id, User.role == UserRole.SCHOOL_ADMIN)
    )
    admin = result.scalar_one_or_none()
    if admin is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="该学校无管理员账户")
    pwd = request.new_password or DEFAULT_PASSWORD
    admin.password_hash = get_password_hash(pwd)
    admin.current_token = ""
    await db.flush()
    return APIResponse.success(message=f"密码已重置为 {pwd}")


@router.post("/batch-reset-password", response_model=APIResponse)
async def batch_reset_school_admin_password(
    request: BatchResetPasswordRequest,
    current_user: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db),
):
    from sqlalchemy import select
    success_count = 0
    fail_count = 0
    pwd = request.new_password or DEFAULT_PASSWORD
    for school_id in request.school_ids:
        result = await db.execute(
            select(User).where(User.school_id == school_id, User.role == UserRole.SCHOOL_ADMIN)
        )
        admin = result.scalar_one_or_none()
        if admin:
            admin.password_hash = get_password_hash(pwd)
            admin.current_token = ""
            success_count += 1
        else:
            fail_count += 1
    await db.flush()
    msg = f"成功重置 {success_count} 个学校管理员密码为 {pwd}"
    if fail_count > 0:
        msg += f"，{fail_count} 个学校无管理员账户"
    return APIResponse.success(message=msg)
