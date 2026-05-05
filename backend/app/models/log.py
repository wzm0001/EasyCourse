import enum
from sqlalchemy import String, Text, Enum
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import BaseModel


class LogType(str, enum.Enum):
    OPERATION = "operation"
    LOGIN = "login"
    SYSTEM = "system"
    SCHEDULE = "schedule"


class LogLevel(str, enum.Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class SystemLog(BaseModel):
    __tablename__ = "system_logs"

    log_type: Mapped[LogType] = mapped_column(Enum(LogType))
    level: Mapped[LogLevel] = mapped_column(Enum(LogLevel), default=LogLevel.INFO)
    user_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    username: Mapped[str] = mapped_column(String(100), default="")
    school_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    action: Mapped[str] = mapped_column(String(200))
    target_type: Mapped[str] = mapped_column(String(100), default="")
    target_id: Mapped[str] = mapped_column(String(36), default="")
    detail: Mapped[str] = mapped_column(Text, default="")
    ip_address: Mapped[str] = mapped_column(String(50), default="")
    stack_trace: Mapped[str] = mapped_column(Text, default="")
