from sqlalchemy import String, Integer, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel


class ScheduleCell(BaseModel):
    __tablename__ = "schedule_cells"

    school_id: Mapped[str] = mapped_column(String(36), ForeignKey("schools.id"))
    semester_id: Mapped[str] = mapped_column(String(36), ForeignKey("semesters.id"))
    grade_id: Mapped[str] = mapped_column(String(36), ForeignKey("grades.id"))
    class_id: Mapped[str] = mapped_column(String(36), ForeignKey("classes.id"))
    day_of_week: Mapped[int] = mapped_column(Integer)
    period_type: Mapped[str] = mapped_column(String(20))
    period_index: Mapped[int] = mapped_column(Integer)
    course_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("courses.id"), nullable=True)
    teacher_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("teachers.id"), nullable=True)
    classroom_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("classrooms.id"), nullable=True)
    is_fixed: Mapped[bool] = mapped_column(Boolean, default=False)

    course: Mapped["Course | None"] = relationship("Course", foreign_keys=[course_id])
    teacher: Mapped["Teacher | None"] = relationship("Teacher", foreign_keys=[teacher_id])
    classroom: Mapped["Classroom | None"] = relationship("Classroom", foreign_keys=[classroom_id])


class ScheduleLock(BaseModel):
    __tablename__ = "schedule_locks"

    school_id: Mapped[str] = mapped_column(String(36), ForeignKey("schools.id"))
    semester_id: Mapped[str] = mapped_column(String(36), ForeignKey("semesters.id"))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))
    locked_at: Mapped[str] = mapped_column(String(30))
