from sqlalchemy import String, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel


class TeachingClass(BaseModel):
    __tablename__ = "teaching_classes"

    school_id: Mapped[str] = mapped_column(String(36), ForeignKey("schools.id"))
    semester_id: Mapped[str] = mapped_column(String(36), ForeignKey("semesters.id"))
    grade_id: Mapped[str] = mapped_column(String(36), ForeignKey("grades.id"))
    name: Mapped[str] = mapped_column(String(200))
    course_id: Mapped[str] = mapped_column(String(36), ForeignKey("courses.id"))
    teacher_id: Mapped[str] = mapped_column(String(36), ForeignKey("teachers.id"))
    classroom_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("classrooms.id"), nullable=True)
    description: Mapped[str] = mapped_column(Text, default="")

    members: Mapped[list["TeachingClassMember"]] = relationship("TeachingClassMember", back_populates="teaching_class")


class TeachingClassMember(BaseModel):
    __tablename__ = "teaching_class_members"

    teaching_class_id: Mapped[str] = mapped_column(String(36), ForeignKey("teaching_classes.id"))
    class_id: Mapped[str] = mapped_column(String(36), ForeignKey("classes.id"))

    teaching_class: Mapped["TeachingClass"] = relationship("TeachingClass", back_populates="members")
