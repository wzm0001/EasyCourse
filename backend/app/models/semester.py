from sqlalchemy import String, Date, Boolean, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import BaseModel


class Semester(BaseModel):
    __tablename__ = "semesters"

    school_id: Mapped[str] = mapped_column(String(36), ForeignKey("schools.id"))
    name: Mapped[str] = mapped_column(String(200))
    start_date: Mapped[str] = mapped_column(Date)
    end_date: Mapped[str] = mapped_column(Date)
    total_weeks: Mapped[int] = mapped_column(Integer, default=20)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False)
    description: Mapped[str] = mapped_column(Text, default="")
