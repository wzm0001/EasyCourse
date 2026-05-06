import enum
from sqlalchemy import String, Enum, Boolean, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel


class UserRole(str, enum.Enum):
    SUPER_ADMIN = "super_admin"
    SCHOOL_ADMIN = "school_admin"
    TEACHER = "teacher"


class AccountStatus(str, enum.Enum):
    ACTIVE = "active"
    PENDING = "pending"
    REJECTED = "rejected"
    DISABLED = "disabled"


class School(BaseModel):
    __tablename__ = "schools"

    name: Mapped[str] = mapped_column(String(200))
    code: Mapped[str] = mapped_column(String(50), unique=True)
    address: Mapped[str] = mapped_column(String(500), default="")
    contact_person: Mapped[str] = mapped_column(String(100), default="")
    contact_phone: Mapped[str] = mapped_column(String(20), default="")
    status: Mapped[AccountStatus] = mapped_column(Enum(AccountStatus), default=AccountStatus.PENDING)
    reject_reason: Mapped[str] = mapped_column(Text, default="")
    school_type: Mapped[str] = mapped_column(String(50), default="middle")
    province: Mapped[str] = mapped_column(String(100), default="")
    city: Mapped[str] = mapped_column(String(100), default="")
    district: Mapped[str] = mapped_column(String(100), default="")
    attachment: Mapped[str] = mapped_column(Text, default="")

    users: Mapped[list["User"]] = relationship("User", back_populates="school")


class User(BaseModel):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    real_name: Mapped[str] = mapped_column(String(100), default="")
    role: Mapped[UserRole] = mapped_column(Enum(UserRole))
    school_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("schools.id"), nullable=True)
    phone: Mapped[str] = mapped_column(String(20), default="")
    email: Mapped[str] = mapped_column(String(200), default="")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    current_token: Mapped[str] = mapped_column(String(500), default="")
    created_by: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)

    school: Mapped[School | None] = relationship("School", back_populates="users")
    creator: Mapped["User | None"] = relationship("User", foreign_keys=[created_by])


class ApprovalRecord(BaseModel):
    __tablename__ = "approval_records"

    type: Mapped[str] = mapped_column(String(50))
    requester_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))
    school_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("schools.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    request_data: Mapped[str] = mapped_column(Text, default="")
    reject_reason: Mapped[str] = mapped_column(Text, default="")
    reviewer_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)

    requester: Mapped["User"] = relationship("User", foreign_keys=[requester_id])
    reviewer: Mapped["User | None"] = relationship("User", foreign_keys=[reviewer_id])
