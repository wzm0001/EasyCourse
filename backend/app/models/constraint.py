import enum
from sqlalchemy import String, Integer, Boolean, ForeignKey, Text, Enum
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import BaseModel


class ConstraintType(str, enum.Enum):
    TEACHER_UNAVAILABLE = "teacher_unavailable"
    CLASSROOM_UNAVAILABLE = "classroom_unavailable"
    COURSE_SPREAD = "course_spread"
    MAX_DAILY_PERIODS = "max_daily_periods"
    MIN_DAILY_GAP = "min_daily_gap"
    NO_CONSECUTIVE = "no_consecutive"
    FIXED_POSITION = "fixed_position"


class ConstraintPriority(str, enum.Enum):
    MANDATORY = "mandatory"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ScheduleConstraint(BaseModel):
    __tablename__ = "schedule_constraints"

    school_id: Mapped[str] = mapped_column(String(36), ForeignKey("schools.id"))
    semester_id: Mapped[str] = mapped_column(String(36), ForeignKey("semesters.id"))
    constraint_type: Mapped[ConstraintType] = mapped_column(Enum(ConstraintType))
    priority: Mapped[ConstraintPriority] = mapped_column(Enum(ConstraintPriority), default=ConstraintPriority.MEDIUM)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    target_type: Mapped[str] = mapped_column(String(20), default="")
    target_id: Mapped[str] = mapped_column(String(36), default="")
    config: Mapped[str] = mapped_column(Text, default="{}")
