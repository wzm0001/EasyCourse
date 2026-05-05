from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.schemas.common import APIResponse, PageResponse
from app.schemas.backup import BackupCreate, BackupInfo
from app.services.backup import create_backup, restore_backup, get_backups, delete_backup, download_backup
from app.middleware.auth import require_super_admin

router = APIRouter(prefix="/backups", tags=["备份管理"])


@router.get("", response_model=APIResponse[PageResponse[BackupInfo]])
async def list_backups(
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await get_backups(page, page_size, db)
    return APIResponse.success(data=result)


@router.post("", response_model=APIResponse[BackupInfo])
async def create_backup_endpoint(
    data: BackupCreate,
    current_user: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db),
):
    record = await create_backup(current_user.id, data.note, db)
    return APIResponse.success(data=BackupInfo.model_validate(record))


@router.post("/{backup_id}/restore", response_model=APIResponse)
async def restore_backup_endpoint(
    backup_id: str,
    current_user: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db),
):
    try:
        await restore_backup(backup_id, current_user.id, db)
        return APIResponse.success(message="备份还原成功")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"还原失败: {str(e)}")


@router.delete("/{backup_id}", response_model=APIResponse)
async def delete_backup_endpoint(
    backup_id: str,
    current_user: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db),
):
    success = await delete_backup(backup_id, db)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="备份记录不存在")
    return APIResponse.success(message="备份删除成功")


@router.get("/{backup_id}/download")
async def download_backup_endpoint(
    backup_id: str,
    current_user: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db),
):
    try:
        filepath = await download_backup(backup_id, db)
        return FileResponse(filepath, filename=filepath.split("/")[-1])
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
