from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.schemas.common import APIResponse
from app.schemas.settings import (
    SettingUpdate,
    SettingInfo,
    DatabaseSwitchRequest,
    DatabaseTestResult,
    PasswordPolicyConfig,
    SystemSettingsInfo,
)
from app.services.settings import (
    get_settings,
    get_all_settings,
    update_setting,
    test_mysql_connection,
    switch_database,
    get_password_policy,
    update_password_policy,
    set_maintenance_mode,
)
from app.middleware.auth import get_current_user_dependency, require_super_admin
from app.middleware.security import generate_csrf_token

router = APIRouter(prefix="/settings", tags=["系统设置"])


@router.get("", response_model=APIResponse)
async def list_settings(
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    from app.models.user import UserRole
    is_super_admin = current_user.role == UserRole.SUPER_ADMIN
    settings_list = await get_all_settings(db, is_super_admin)
    return APIResponse.success(data=settings_list)


@router.put("", response_model=APIResponse[SettingInfo])
async def update_settings(
    data: SettingUpdate,
    current_user: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db),
):
    setting = await update_setting(data.key, data.value, db)
    return APIResponse.success(data=setting)


@router.post("/test-mysql", response_model=APIResponse[DatabaseTestResult])
async def test_mysql(
    request: DatabaseSwitchRequest,
    current_user: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await test_mysql_connection(
        request.mysql_host or "localhost",
        request.mysql_port or 3306,
        request.mysql_user or "root",
        request.mysql_password or "",
        request.mysql_database or "scheduling",
    )
    return APIResponse.success(data=result)


@router.post("/switch-database", response_model=APIResponse)
async def switch_db(
    request: DatabaseSwitchRequest,
    current_user: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await switch_database(request, db)
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"],
        )
    return APIResponse.success(message=result["message"])


@router.get("/password-policy", response_model=APIResponse[PasswordPolicyConfig])
async def get_pwd_policy(
    db: AsyncSession = Depends(get_db),
):
    policy = await get_password_policy(db)
    return APIResponse.success(data=policy)


@router.put("/password-policy", response_model=APIResponse[PasswordPolicyConfig])
async def update_pwd_policy(
    config: PasswordPolicyConfig,
    current_user: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db),
):
    policy = await update_password_policy(config, db)
    return APIResponse.success(data=policy)


@router.post("/maintenance", response_model=APIResponse)
async def toggle_maintenance(
    enabled: bool,
    current_user: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db),
):
    await set_maintenance_mode(enabled, db)
    message = "维护模式已开启" if enabled else "维护模式已关闭"
    return APIResponse.success(message=message)


security_router = APIRouter(prefix="/security", tags=["安全"])


@security_router.get("/csrf-token", response_model=APIResponse)
async def get_csrf_token():
    token = generate_csrf_token()
    return APIResponse.success(data={"csrf_token": token})
