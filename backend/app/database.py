import logging
import re

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text
from typing import AsyncGenerator

from app.config import settings

logger = logging.getLogger(__name__)

_IDENTIFIER_PATTERN = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")


def create_db_engine():
    if settings.DATABASE_TYPE == "mysql":
        url = f"mysql+aiomysql://{settings.MYSQL_USER}:{settings.MYSQL_PASSWORD}@{settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{settings.MYSQL_DATABASE}"
        return create_async_engine(url, echo=settings.DEBUG, pool_pre_ping=True)
    else:
        url = f"sqlite+aiosqlite:///{settings.SQLITE_PATH}"
        return create_async_engine(
            url,
            echo=settings.DEBUG,
            connect_args={"check_same_thread": False},
        )


engine = create_db_engine()

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def _migrate_add_columns(conn):
    migrations = [
        ("grades", "morning_reading_count", "INTEGER DEFAULT 1"),
        ("grades", "regular_class_count", "INTEGER DEFAULT 8"),
        ("grades", "evening_study_count", "INTEGER DEFAULT 0"),
        ("schedule_cells", "is_locked", "BOOLEAN DEFAULT 0"),
        ("grade_courses", "weekly_hours", "INTEGER DEFAULT 1"),
        ("grade_courses", "period_type", "VARCHAR(50) DEFAULT 'regular'"),
        ("teaching_arrangements", "continuous_hours", "INTEGER DEFAULT 1"),
        ("teachers", "specialization", "TEXT DEFAULT ''"),
        ("classrooms", "building_name", "VARCHAR(100) DEFAULT ''"),
        ("classrooms", "room_number", "VARCHAR(50) DEFAULT ''"),
        ("classrooms", "code", "VARCHAR(50) DEFAULT ''"),
        ("users", "must_change_password", "BOOLEAN DEFAULT 0"),
    ]

    for table, column, col_type in migrations:
        if not _IDENTIFIER_PATTERN.match(table):
            raise ValueError(f"非法表名: {table}")
        if not _IDENTIFIER_PATTERN.match(column):
            raise ValueError(f"非法列名: {column}")

    failed_migrations = []
    for table, column, col_type in migrations:
        try:
            await conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}"))
            logger.info(f"迁移成功: {table}.{column}")
        except Exception as e:
            err_msg = str(e).lower()
            if "duplicate column" in err_msg or "already exists" in err_msg:
                logger.debug(f"列已存在，跳过: {table}.{column}")
            else:
                logger.warning(f"迁移失败: {table}.{column}, 错误: {e}")
                failed_migrations.append((table, column, str(e)))

    if failed_migrations:
        details = ", ".join(f"{t}.{c}" for t, c, _ in failed_migrations)
        raise RuntimeError(f"数据库迁移失败，以下列添加出错: {details}")


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await _migrate_add_columns(conn)


async def close_db():
    await engine.dispose()
