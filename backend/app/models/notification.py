import enum
from sqlalchemy import String, Text, Boolean, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import BaseModel


class NotificationType(str, enum.Enum):
    SCHOOL_REGISTRATION = "school_registration"
    APPROVAL_RESULT = "approval_result"
    SCHEDULE_COMPLETE = "schedule_complete"
    SYSTEM_MAINTENANCE = "system_maintenance"
    DATA_CHANGE_APPROVAL = "data_change_approval"


class Notification(BaseModel):
    __tablename__ = "notifications"

    school_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("schools.id"), nullable=True)
    type: Mapped[NotificationType] = mapped_column(Enum(NotificationType))
    title: Mapped[str] = mapped_column(String(200))
    content: Mapped[str] = mapped_column(Text)
    sender_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    receiver_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
