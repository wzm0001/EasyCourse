from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.models.backup import BackupStatus


class BackupInfo(BaseModel):
    id: str
    filename: str
    file_size: int = 0
    status: BackupStatus
    operator_id: str
    note: str = ""
    created_at: datetime

    model_config = {"from_attributes": True}


class BackupCreate(BaseModel):
    note: Optional[str] = None


class BackupRestore(BaseModel):
    backup_id: str
    confirm: bool
