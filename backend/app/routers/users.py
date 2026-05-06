from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User, UserRole
from app.schemas.common import APIResponse, PageResponse
from app.schemas.user import UserInfo, TeacherCreate, UserUpdate, UserStatusUpdate, ResetPasswordRequest, AdminCreateRequest
from app.repositories.user import UserRepository
from app.services.user import create_teacher, update_user_profile
from app.services.auth import validate_password_strength
from app.middleware.auth import require_super_admin, require_school_admin, get_current_user_dependency
from app.middleware.tenant import get_tenant_filter

router = APIRouter(prefix="/users", tags=["用户管理"])


@router.get("", response_model=APIResponse[PageResponse[UserInfo]])
async def get_users(
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    user_repo = UserRepository(db)
    if current_user.role == UserRole.SUPER_ADMIN:
        users, total = await user_repo.get_admin_users(page=page, page_size=page_size)
    else:
        if not current_user.school_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")
        users, total = await user_repo.get_by_school(current_user.school_id, page=page, page_size=page_size)
    items = []
    for u in users:
        school_name = None
        if u.school_id:
            from app.repositories.user import SchoolRepository
            school_repo = SchoolRepository(db)
            school = await school_repo.get_by_id(u.school_id)
            if school:
                school_name = school.name
        items.append(UserInfo(
            id=u.id,
            username=u.username,
            real_name=u.real_name,
            role=u.role,
            school_id=u.school_id,
            school_name=school_name,
            phone=u.phone,
            email=u.email,
            is_active=u.is_active,
            created_by=u.created_by,
        ))
    return APIResponse.success(data=PageResponse(items=items, total=total, page=page, page_size=page_size))


@router.post("/admin", response_model=APIResponse[UserInfo])
async def create_admin_endpoint(
    request: AdminCreateRequest,
    current_user: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db),
):
    if not validate_password_strength(request.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="密码强度不足：至少8位，需包含大小写字母和数字",
        )
    user_repo = UserRepository(db)
    existing = await user_repo.get_by_username(request.username)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户名已存在")
    from app.services.auth import get_password_hash
    admin_user = User(
        username=request.username,
        password_hash=get_password_hash(request.password),
        real_name=request.real_name,
        role=UserRole.SUPER_ADMIN,
        created_by=current_user.id,
        is_active=True,
        phone=request.phone,
        email=request.email,
    )
    await user_repo.create(admin_user)
    user_info = UserInfo(
        id=admin_user.id,
        username=admin_user.username,
        real_name=admin_user.real_name,
        role=admin_user.role,
        school_id=admin_user.school_id,
        school_name=None,
        phone=admin_user.phone,
        email=admin_user.email,
        is_active=admin_user.is_active,
        created_by=admin_user.created_by,
    )
    return APIResponse.success(data=user_info)


@router.post("/teachers", response_model=APIResponse[UserInfo])
async def create_teacher_endpoint(
    request: TeacherCreate,
    current_user: User = Depends(require_school_admin),
    db: AsyncSession = Depends(get_db),
):
    if not current_user.school_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="当前用户未关联学校")
    if not validate_password_strength(request.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="密码强度不足：至少8位，需包含大小写字母和数字",
        )
    user_repo = UserRepository(db)
    existing = await user_repo.get_by_username(request.username)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户名已存在")
    teacher = await create_teacher(request.model_dump(), current_user.school_id, db)
    school_name = None
    if teacher.school_id:
        from app.repositories.user import SchoolRepository
        school_repo = SchoolRepository(db)
        school = await school_repo.get_by_id(teacher.school_id)
        if school:
            school_name = school.name
    user_info = UserInfo(
        id=teacher.id,
        username=teacher.username,
        real_name=teacher.real_name,
        role=teacher.role,
        school_id=teacher.school_id,
        school_name=school_name,
        phone=teacher.phone,
        email=teacher.email,
        is_active=teacher.is_active,
    )
    return APIResponse.success(data=user_info)


@router.put("/{user_id}", response_model=APIResponse)
async def update_user(
    user_id: str,
    request: UserUpdate,
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    user_repo = UserRepository(db)
    target_user = await user_repo.get_by_id(user_id)
    if target_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    if current_user.role != UserRole.SUPER_ADMIN:
        if current_user.role == UserRole.SCHOOL_ADMIN:
            if target_user.school_id != current_user.school_id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")
            if target_user.role == UserRole.SUPER_ADMIN:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")
        else:
            if current_user.id != user_id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")
    if request.username and request.username != target_user.username:
        existing = await user_repo.get_by_username(request.username)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已存在",
            )
    if request.password and not validate_password_strength(request.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="密码强度不足：至少8位，需包含大小写字母和数字",
        )
    await update_user_profile(user_id, request.model_dump(), db)
    return APIResponse.success(message="用户信息更新成功")


@router.put("/{user_id}/password", response_model=APIResponse)
async def reset_password(
    user_id: str,
    request: ResetPasswordRequest,
    current_user: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db),
):
    if not validate_password_strength(request.new_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="密码强度不足：至少8位，需包含大小写字母和数字",
        )
    user_repo = UserRepository(db)
    target_user = await user_repo.get_by_id(user_id)
    if target_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    if target_user.created_by != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")
    from app.services.auth import get_password_hash
    await user_repo.update(user_id, {"password_hash": get_password_hash(request.new_password)})
    return APIResponse.success(message="密码重置成功")


@router.put("/{user_id}/status", response_model=APIResponse)
async def update_user_status(
    user_id: str,
    request: UserStatusUpdate,
    current_user: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db),
):
    user_repo = UserRepository(db)
    target_user = await user_repo.get_by_id(user_id)
    if target_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    if target_user.created_by != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")
    await user_repo.update(user_id, {"is_active": request.is_active})
    return APIResponse.success(message="用户状态更新成功")
