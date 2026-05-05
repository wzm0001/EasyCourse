import json
import os
from typing import List

from sqlalchemy import select, inspect
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.config import settings
from app.models.settings import SystemSetting
from app.repositories.settings import SystemSettingRepository
from app.schemas.settings import (
    SystemSettingsInfo,
    PasswordPolicyConfig,
    DatabaseTestResult,
    DatabaseSwitchRequest,
    SettingInfo,
)


async def get_settings(db: AsyncSession, is_super_admin: bool = False) -> SystemSettingsInfo:
    repo = SystemSettingRepository(db)
    password_policy = await get_password_policy(db)

    maintenance_setting = await repo.get_by_key("maintenance_mode")
    maintenance_mode = maintenance_setting.value == "true" if maintenance_setting else False

    auto_backup_setting = await repo.get_by_key("auto_backup_enabled")
    auto_backup_enabled = auto_backup_setting.value == "true" if auto_backup_setting else True

    auto_backup_cron_setting = await repo.get_by_key("auto_backup_cron")
    auto_backup_cron = auto_backup_cron_setting.value if auto_backup_cron_setting else "0 2 * * *"

    return SystemSettingsInfo(
        database_type=settings.DATABASE_TYPE,
        password_policy=password_policy,
        token_expire_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        maintenance_mode=maintenance_mode,
        auto_backup_enabled=auto_backup_enabled,
        auto_backup_cron=auto_backup_cron,
    )


async def get_all_settings(db: AsyncSession, is_super_admin: bool = False) -> List[SettingInfo]:
    repo = SystemSettingRepository(db)
    if is_super_admin:
        result = await db.execute(select(SystemSetting))
        settings_list = list(result.scalars().all())
    else:
        settings_list = await repo.get_public_settings()
    return [SettingInfo.model_validate(s) for s in settings_list]


async def update_setting(key: str, value: str, db: AsyncSession) -> SettingInfo:
    repo = SystemSettingRepository(db)
    setting = await repo.upsert(key, value)
    await db.flush()
    return SettingInfo.model_validate(setting)


async def test_mysql_connection(
    host: str, port: int, user: str, password: str, database: str
) -> DatabaseTestResult:
    try:
        url = f"mysql+aiomysql://{user}:{password}@{host}:{port}/{database}"
        test_engine = create_async_engine(url, pool_pre_ping=True)
        async with test_engine.connect() as conn:
            await conn.execute(select(1))
        await test_engine.dispose()
        return DatabaseTestResult(success=True, message="MySQL连接成功")
    except Exception as e:
        return DatabaseTestResult(success=False, message=f"MySQL连接失败: {str(e)}")


async def switch_database(request: DatabaseSwitchRequest, db: AsyncSession) -> dict:
    if request.database_type not in ("sqlite", "mysql"):
        return {"success": False, "message": "不支持的数据库类型"}

    if request.database_type == "mysql":
        if not all([request.mysql_host, request.mysql_user, request.mysql_database]):
            return {"success": False, "message": "MySQL配置不完整"}

        test_result = await test_mysql_connection(
            request.mysql_host,
            request.mysql_port or 3306,
            request.mysql_user,
            request.mysql_password or "",
            request.mysql_database,
        )
        if not test_result.success:
            return {"success": False, "message": test_result.message}

    from app.database import Base

    source_engine = None
    target_engine = None

    try:
        if request.database_type == "mysql" and settings.DATABASE_TYPE == "sqlite":
            source_url = f"sqlite+aiosqlite:///{settings.SQLITE_PATH}"
            target_url = f"mysql+aiomysql://{request.mysql_user}:{request.mysql_password}@{request.mysql_host}:{request.mysql_port or 3306}/{request.mysql_database}"
        elif request.database_type == "sqlite" and settings.DATABASE_TYPE == "mysql":
            source_url = f"mysql+aiomysql://{settings.MYSQL_USER}:{settings.MYSQL_PASSWORD}@{settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{settings.MYSQL_DATABASE}"
            target_url = f"sqlite+aiosqlite:///{settings.SQLITE_PATH}"
        else:
            if request.database_type == "mysql":
                target_url = f"mysql+aiomysql://{request.mysql_user}:{request.mysql_password}@{request.mysql_host}:{request.mysql_port or 3306}/{request.mysql_database}"
            else:
                return {"success": False, "message": "不支持的数据库切换操作"}

        source_engine = create_async_engine(source_url)
        target_engine = create_async_engine(target_url)

        async with target_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        table_names = []
        async with source_engine.connect() as conn:
            def _get_table_names(connection):
                insp = inspect(connection)
                return insp.get_table_names()
            table_names = await conn.run_sync(_get_table_names)

        source_session_factory = async_sessionmaker(source_engine, class_=AsyncSession, expire_on_commit=False)
        target_session_factory = async_sessionmaker(target_engine, class_=AsyncSession, expire_on_commit=False)

        for table_name in table_names:
            if table_name == "system_settings":
                continue
            async with source_session_factory() as src_session:
                result = await src_session.execute(select(Base.metadata.tables[table_name]))
                rows = result.fetchall()

            if rows:
                async with target_session_factory() as tgt_session:
                    for row in rows:
                        row_dict = row._mapping
                        columns = list(row_dict.keys())
                        values = list(row_dict.values())
                        from sqlalchemy import insert as sa_insert
                        stmt = sa_insert(Base.metadata.tables[table_name]).values(
                            dict(zip(columns, values))
                        )
                        await tgt_session.execute(stmt)
                    await tgt_session.commit()

        _update_env_file(request)

        return {
            "success": True,
            "message": "数据库切换成功，请重启后端服务以使配置生效",
        }
    except Exception as e:
        return {"success": False, "message": f"数据库切换失败: {str(e)}"}
    finally:
        if source_engine:
            await source_engine.dispose()
        if target_engine:
            await target_engine.dispose()


def _update_env_file(request: DatabaseSwitchRequest):
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env")
    env_lines = []
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            env_lines = f.readlines()

    env_dict = {}
    for line in env_lines:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            env_dict[key.strip()] = value.strip()

    env_dict["DATABASE_TYPE"] = request.database_type
    if request.database_type == "mysql":
        if request.mysql_host:
            env_dict["MYSQL_HOST"] = request.mysql_host
        if request.mysql_port:
            env_dict["MYSQL_PORT"] = str(request.mysql_port)
        if request.mysql_user:
            env_dict["MYSQL_USER"] = request.mysql_user
        if request.mysql_password is not None:
            env_dict["MYSQL_PASSWORD"] = request.mysql_password
        if request.mysql_database:
            env_dict["MYSQL_DATABASE"] = request.mysql_database

    with open(env_path, "w", encoding="utf-8") as f:
        for key, value in env_dict.items():
            f.write(f"{key}={value}\n")


async def get_password_policy(db: AsyncSession) -> PasswordPolicyConfig:
    repo = SystemSettingRepository(db)
    setting = await repo.get_by_key("password_policy")
    if setting and setting.value:
        try:
            data = json.loads(setting.value)
            return PasswordPolicyConfig(**data)
        except (json.JSONDecodeError, TypeError):
            pass
    return PasswordPolicyConfig()


async def update_password_policy(config: PasswordPolicyConfig, db: AsyncSession) -> PasswordPolicyConfig:
    repo = SystemSettingRepository(db)
    await repo.upsert("password_policy", config.model_dump_json(), "密码策略配置", False)
    await db.flush()
    return config


async def set_maintenance_mode(enabled: bool, db: AsyncSession):
    repo = SystemSettingRepository(db)
    await repo.upsert("maintenance_mode", "true" if enabled else "false", "维护模式", True)
    await db.flush()


async def is_maintenance_mode(db: AsyncSession) -> bool:
    repo = SystemSettingRepository(db)
    setting = await repo.get_by_key("maintenance_mode")
    return setting.value == "true" if setting else False
