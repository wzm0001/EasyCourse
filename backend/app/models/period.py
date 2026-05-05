import enum
from sqlalchemy import String, Integer, Boolean, ForeignKey, Enum, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import BaseModel


class PeriodType(str, enum.Enum):
    MORNING_READING = "morning_reading"
    REGULAR = "regular"
    EVENING_STUDY = "evening_study"


class GradePeriodConfig(BaseModel):
    __tablename__ = "grade_period_configs"

    school_id: Mapped[str] = mapped_column(String(36), ForeignKey("schools.id"))
    semester_id: Mapped[str] = mapped_column(String(36), ForeignKey("semesters.id"))
    grade_id: Mapped[str] = mapped_column(String(36), ForeignKey("grades.id"))
    period_type: Mapped[PeriodType] = mapped_column(Enum(PeriodType))
    period_index: Mapped[int] = mapped_column(Integer)
    start_time: Mapped[str] = mapped_column(String(8))
    end_time: Mapped[str] = mapped_column(String(8))


class DayPeriodConfig(BaseModel):
    __tablename__ = "day_period_configs"

    school_id: Mapped[str] = mapped_column(String(36), ForeignKey("schools.id"))
    semester_id: Mapped[str] = mapped_column(String(36), ForeignKey("semesters.id"))
    grade_id: Mapped[str] = mapped_column(String(36), ForeignKey("grades.id"))
    day_of_week: Mapped[int] = mapped_column(Integer)
    period_type: Mapped[PeriodType] = mapped_column(Enum(PeriodType))
    period_index: Mapped[int] = mapped_column(Integer)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)


class PeriodTemplate(BaseModel):
    __tablename__ = "period_templates"

    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text, default="")
    config_data: Mapped[str] = mapped_column(Text)
    is_system: Mapped[bool] = mapped_column(Boolean, default=False)
