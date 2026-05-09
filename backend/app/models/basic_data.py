import enum
from sqlalchemy import String, Integer, Boolean, ForeignKey, Enum, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel
from app.models.period import PeriodType


class CourseType(str, enum.Enum):
    REQUIRED = "required"
    ELECTIVE = "elective"


class Grade(BaseModel):
    __tablename__ = "grades"

    school_id: Mapped[str] = mapped_column(String(36), ForeignKey("schools.id"))
    semester_id: Mapped[str] = mapped_column(String(36), ForeignKey("semesters.id"))
    name: Mapped[str] = mapped_column(String(100))
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    morning_reading_count: Mapped[int] = mapped_column(Integer, default=1)
    regular_class_count: Mapped[int] = mapped_column(Integer, default=8)
    evening_study_count: Mapped[int] = mapped_column(Integer, default=0)
    grade_leader_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("teachers.id"), nullable=True)

    classes: Mapped[list["Class_"]] = relationship("Class_", back_populates="grade")
    courses: Mapped[list["GradeCourse"]] = relationship("GradeCourse", back_populates="grade")
    grade_leader: Mapped["Teacher | None"] = relationship("Teacher", foreign_keys=[grade_leader_id])


class Class_(BaseModel):
    __tablename__ = "classes"

    school_id: Mapped[str] = mapped_column(String(36), ForeignKey("schools.id"))
    semester_id: Mapped[str] = mapped_column(String(36), ForeignKey("semesters.id"))
    grade_id: Mapped[str] = mapped_column(String(36), ForeignKey("grades.id"))
    name: Mapped[str] = mapped_column(String(100))
    head_teacher_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("teachers.id"), nullable=True)
    classroom_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("classrooms.id"), nullable=True)
    is_teaching_class: Mapped[bool] = mapped_column(Boolean, default=False)

    grade: Mapped["Grade"] = relationship("Grade", back_populates="classes")
    head_teacher: Mapped["Teacher | None"] = relationship("Teacher", foreign_keys=[head_teacher_id])
    classroom: Mapped["Classroom | None"] = relationship("Classroom", foreign_keys=[classroom_id])


class Course(BaseModel):
    __tablename__ = "courses"

    school_id: Mapped[str] = mapped_column(String(36), ForeignKey("schools.id"))
    code: Mapped[str] = mapped_column(String(50), default="")
    name: Mapped[str] = mapped_column(String(100))
    course_type: Mapped[CourseType] = mapped_column(Enum(CourseType), default=CourseType.REQUIRED)
    weekly_hours: Mapped[int] = mapped_column(Integer, default=1)


class GradeCourse(BaseModel):
    __tablename__ = "grade_courses"

    school_id: Mapped[str] = mapped_column(String(36), ForeignKey("schools.id"))
    semester_id: Mapped[str] = mapped_column(String(36), ForeignKey("semesters.id"))
    grade_id: Mapped[str] = mapped_column(String(36), ForeignKey("grades.id"))
    course_id: Mapped[str] = mapped_column(String(36), ForeignKey("courses.id"))
    weekly_hours: Mapped[int] = mapped_column(Integer, default=1)
    period_type: Mapped[PeriodType] = mapped_column(Enum(PeriodType), default=PeriodType.REGULAR)

    grade: Mapped["Grade"] = relationship("Grade", back_populates="courses")
    course: Mapped["Course"] = relationship("Course")


class Teacher(BaseModel):
    __tablename__ = "teachers"

    school_id: Mapped[str] = mapped_column(String(36), ForeignKey("schools.id"))
    semester_id: Mapped[str] = mapped_column(String(36), ForeignKey("semesters.id"))
    user_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(100))
    employee_id: Mapped[str] = mapped_column(String(50), default="")
    gender: Mapped[str] = mapped_column(String(10), default="")
    phone: Mapped[str] = mapped_column(String(20), default="")
    teaching_group: Mapped[str] = mapped_column(String(100), default="")
    specialization: Mapped[str] = mapped_column(Text, default="")


class TeacherCourse(BaseModel):
    __tablename__ = "teacher_courses"

    school_id: Mapped[str] = mapped_column(String(36), ForeignKey("schools.id"))
    semester_id: Mapped[str] = mapped_column(String(36), ForeignKey("semesters.id"))
    teacher_id: Mapped[str] = mapped_column(String(36), ForeignKey("teachers.id"))
    course_id: Mapped[str] = mapped_column(String(36), ForeignKey("courses.id"))


class Classroom(BaseModel):
    __tablename__ = "classrooms"
    __table_args__ = (
        UniqueConstraint("school_id", "semester_id", "code", name="uq_classroom_code"),
    )

    school_id: Mapped[str] = mapped_column(String(36), ForeignKey("schools.id"))
    semester_id: Mapped[str] = mapped_column(String(36), ForeignKey("semesters.id"))
    building_name: Mapped[str] = mapped_column(String(100))
    room_number: Mapped[str] = mapped_column(String(50))
    code: Mapped[str] = mapped_column(String(50))
    room_type: Mapped[str] = mapped_column(String(50), default="normal")
    capacity: Mapped[int] = mapped_column(Integer, default=50)


class ClassroomCourse(BaseModel):
    __tablename__ = "classroom_courses"

    school_id: Mapped[str] = mapped_column(String(36), ForeignKey("schools.id"))
    semester_id: Mapped[str] = mapped_column(String(36), ForeignKey("semesters.id"))
    classroom_id: Mapped[str] = mapped_column(String(36), ForeignKey("classrooms.id"))
    course_id: Mapped[str] = mapped_column(String(36), ForeignKey("courses.id"))


class TeachingArrangement(BaseModel):
    __tablename__ = "teaching_arrangements"

    school_id: Mapped[str] = mapped_column(String(36), ForeignKey("schools.id"))
    semester_id: Mapped[str] = mapped_column(String(36), ForeignKey("semesters.id"))
    teacher_id: Mapped[str] = mapped_column(String(36), ForeignKey("teachers.id"))
    course_id: Mapped[str] = mapped_column(String(36), ForeignKey("courses.id"))
    class_id: Mapped[str] = mapped_column(String(36), ForeignKey("classes.id"))
    weekly_hours: Mapped[int] = mapped_column(Integer, default=1)
    continuous_hours: Mapped[int] = mapped_column(Integer, default=1)
