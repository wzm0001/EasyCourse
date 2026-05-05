import enum
from sqlalchemy import String, Integer, Enum, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import BaseModel


class BackupStatus(str, enum.Enum):
    COMPLETED = "completed"
    FAILED = "failed"


class BackupRecord(BaseModel):
    __tablename__ = "backup_records"

    filename: Mapped[str] = mapped_column(String(500))
    file_size: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[BackupStatus] = mapped_column(Enum(BackupStatus))
    operator_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))
    note: Mapped[str] = mapped_column(Text, default="")
