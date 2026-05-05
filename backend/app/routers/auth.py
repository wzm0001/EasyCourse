from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User, UserRole, AccountStatus
from app.schemas.common import APIResponse
from app.schemas.user import LoginRequest, LoginResponse, UserInfo, SchoolCreate, ChangePasswordRequest, VerifyIdentityRequest, ResetPasswordRequest
from app.services.auth import authenticate_user, create_access_token, validate_password_strength
from app.services.user import register_school, change_password
from app.repositories.user import UserRepository, SchoolRepository
from app.middleware.auth import get_current_user_dependency

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/login", response_model=APIResponse[LoginResponse])
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(request.username, request.password, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用",
        )
    if user.role == UserRole.SCHOOL_ADMIN:
        school_repo = SchoolRepository(db)
        school = await school_repo.get_by_id(user.school_id)
        if school and school.status != AccountStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="学校账户尚未通过审批",
            )
    token = create_access_token(data={"sub": user.id})
    user.current_token = token
    await db.flush()
    school_name = None
    if user.school_id:
        school_repo = SchoolRepository(db)
        school = await school_repo.get_by_id(user.school_id)
        if school:
            school_name = school.name
    user_info = UserInfo(
        id=user.id,
        username=user.username,
        real_name=user.real_name,
        role=user.role,
        school_id=user.school_id,
        school_name=school_name,
        phone=user.phone,
        email=user.email,
        is_active=user.is_active,
    )
    return APIResponse.success(data=LoginResponse(access_token=token, user=user_info))


@router.post("/register", response_model=APIResponse)
async def register(request: SchoolCreate, db: AsyncSession = Depends(get_db)):
    user_repo = UserRepository(db)
    existing = await user_repo.get_by_username(request.code)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该学校编码已被注册",
        )
    school_repo = SchoolRepository(db)
    existing_school = await school_repo.get_by_code(request.code)
    if existing_school:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该学校编码已被注册",
        )
    from app.services.auth import get_password_hash
    school = await register_school(request.model_dump(), db)
    admin_user = User(
        username=request.code,
        password_hash=get_password_hash(request.code + "@123"),
        real_name=request.contact_person,
        role=UserRole.SCHOOL_ADMIN,
        school_id=school.id,
        phone=request.contact_phone,
        is_active=False,
    )
    await user_repo.create(admin_user)
    return APIResponse.success(message="注册申请已提交，请等待审批")


@router.get("/me", response_model=APIResponse[UserInfo])
async def get_me(current_user: User = Depends(get_current_user_dependency), db: AsyncSession = Depends(get_db)):
    school_name = None
    if current_user.school_id:
        school_repo = SchoolRepository(db)
        school = await school_repo.get_by_id(current_user.school_id)
        if school:
            school_name = school.name
    user_info = UserInfo(
        id=current_user.id,
        username=current_user.username,
        real_name=current_user.real_name,
        role=current_user.role,
        school_id=current_user.school_id,
        school_name=school_name,
        phone=current_user.phone,
        email=current_user.email,
        is_active=current_user.is_active,
    )
    return APIResponse.success(data=user_info)


@router.put("/change-password", response_model=APIResponse)
async def change_password_endpoint(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    if not validate_password_strength(request.new_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="密码强度不足：至少8位，需包含大小写字母和数字",
        )
    success = await change_password(current_user.id, request.old_password, request.new_password, db)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="原密码错误",
        )
    return APIResponse.success(message="密码修改成功")


@router.post("/verify-identity", response_model=APIResponse)
async def verify_identity(request: VerifyIdentityRequest, db: AsyncSession = Depends(get_db)):
    user_repo = UserRepository(db)
    user = await user_repo.get_by_username(request.username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在",
        )
    if user.phone != request.phone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="手机号与注册信息不匹配",
        )
    return APIResponse.success(data={"verified": True})


@router.put("/reset-password", response_model=APIResponse)
async def reset_password(request: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    if not validate_password_strength(request.new_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="密码强度不足：至少8位，需包含大小写字母和数字",
        )
    user_repo = UserRepository(db)
    user = await user_repo.get_by_username(request.username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在",
        )
    from app.services.auth import get_password_hash
    user.password_hash = get_password_hash(request.new_password)
    user.current_token = ""
    await db.flush()
    return APIResponse.success(message="密码重置成功")
