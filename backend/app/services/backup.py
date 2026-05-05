import os
import shutil
import subprocess
from datetime import datetime
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings
from app.models.backup import BackupRecord, BackupStatus
from app.models.log import LogLevel
from app.repositories.backup import BackupRecordRepository
from app.schemas.backup import BackupInfo
from app.schemas.common import PageResponse
from app.services.log import log_system


async def create_backup(operator_id: str, note: Optional[str], db: AsyncSession) -> BackupRecord:
    repo = BackupRecordRepository(db)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs(settings.BACKUP_DIR, exist_ok=True)

    if settings.DATABASE_TYPE == "mysql":
        filename = f"backup_mysql_{timestamp}.sql"
        filepath = os.path.join(settings.BACKUP_DIR, filename)
        try:
            cmd = [
                "mysqldump",
                f"-h{settings.MYSQL_HOST}",
                f"-P{settings.MYSQL_PORT}",
                f"-u{settings.MYSQL_USER}",
                f"-p{settings.MYSQL_PASSWORD}",
                settings.MYSQL_DATABASE,
            ]
            with open(filepath, "w") as f:
                proc = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE)
            if proc.returncode != 0:
                raise RuntimeError(proc.stderr.decode())
            file_size = os.path.getsize(filepath)
            record = BackupRecord(
                filename=filename,
                file_size=file_size,
                status=BackupStatus.COMPLETED,
                operator_id=operator_id,
                note=note or "",
            )
            record = await repo.create(record)
            await log_system(LogLevel.INFO, "创建备份", f"MySQL备份成功: {filename}", "", db)
            return record
        except Exception as e:
            if os.path.exists(filepath):
                os.remove(filepath)
            record = BackupRecord(
                filename=filename,
                file_size=0,
                status=BackupStatus.FAILED,
                operator_id=operator_id,
                note=note or "",
            )
            record = await repo.create(record)
            await log_system(LogLevel.ERROR, "创建备份失败", str(e), "", db)
            return record
    else:
        filename = f"backup_sqlite_{timestamp}.db"
        filepath = os.path.join(settings.BACKUP_DIR, filename)
        try:
            shutil.copy2(settings.SQLITE_PATH, filepath)
            file_size = os.path.getsize(filepath)
            record = BackupRecord(
                filename=filename,
                file_size=file_size,
                status=BackupStatus.COMPLETED,
                operator_id=operator_id,
                note=note or "",
            )
            record = await repo.create(record)
            await log_system(LogLevel.INFO, "创建备份", f"SQLite备份成功: {filename}", "", db)
            return record
        except Exception as e:
            if os.path.exists(filepath):
                os.remove(filepath)
            record = BackupRecord(
                filename=filename,
                file_size=0,
                status=BackupStatus.FAILED,
                operator_id=operator_id,
                note=note or "",
            )
            record = await repo.create(record)
            await log_system(LogLevel.ERROR, "创建备份失败", str(e), "", db)
            return record


async def restore_backup(backup_id: str, operator_id: str, db: AsyncSession) -> BackupRecord:
    repo = BackupRecordRepository(db)
    record = await repo.get_by_id(backup_id)
    if record is None:
        raise ValueError("备份记录不存在")
    filepath = os.path.join(settings.BACKUP_DIR, record.filename)
    if not os.path.exists(filepath):
        raise FileNotFoundError("备份文件不存在")

    if settings.DATABASE_TYPE == "mysql":
        try:
            cmd = [
                "mysql",
                f"-h{settings.MYSQL_HOST}",
                f"-P{settings.MYSQL_PORT}",
                f"-u{settings.MYSQL_USER}",
                f"-p{settings.MYSQL_PASSWORD}",
                settings.MYSQL_DATABASE,
            ]
            with open(filepath, "r") as f:
                proc = subprocess.run(cmd, stdin=f, stderr=subprocess.PIPE)
            if proc.returncode != 0:
                raise RuntimeError(proc.stderr.decode())
            await log_system(LogLevel.INFO, "还原备份", f"MySQL还原成功: {record.filename}", "", db)
            return record
        except Exception as e:
            await log_system(LogLevel.ERROR, "还原备份失败", str(e), "", db)
            raise
    else:
        try:
            shutil.copy2(filepath, settings.SQLITE_PATH)
            await log_system(LogLevel.INFO, "还原备份", f"SQLite还原成功: {record.filename}", "", db)
            return record
        except Exception as e:
            await log_system(LogLevel.ERROR, "还原备份失败", str(e), "", db)
            raise


async def get_backups(page: int, page_size: int, db: AsyncSession) -> PageResponse[BackupInfo]:
    repo = BackupRecordRepository(db)
    items, total = await repo.get_all_ordered(page=page, page_size=page_size)
    backup_infos = [BackupInfo.model_validate(item) for item in items]
    return PageResponse(items=backup_infos, total=total, page=page, page_size=page_size)


async def delete_backup(backup_id: str, db: AsyncSession) -> bool:
    repo = BackupRecordRepository(db)
    record = await repo.get_by_id(backup_id)
    if record is None:
        return False
    filepath = os.path.join(settings.BACKUP_DIR, record.filename)
    if os.path.exists(filepath):
        os.remove(filepath)
    await repo.delete(backup_id)
    return True


async def download_backup(backup_id: str, db: AsyncSession) -> str:
    repo = BackupRecordRepository(db)
    record = await repo.get_by_id(backup_id)
    if record is None:
        raise ValueError("备份记录不存在")
    filepath = os.path.join(settings.BACKUP_DIR, record.filename)
    if not os.path.exists(filepath):
        raise FileNotFoundError("备份文件不存在")
    return filepath


def setup_auto_backup(db_session_factory):
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
    from app.database import AsyncSessionLocal

    scheduler = AsyncIOScheduler()

    async def auto_backup_job():
        async with AsyncSessionLocal() as db:
            try:
                await create_backup("system", "自动备份", db)
                await db.commit()
            except Exception:
                await db.rollback()

    scheduler.add_job(auto_backup_job, "cron", hour=2, minute=0)
    scheduler.start()
    return scheduler
