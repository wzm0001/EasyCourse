from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.models.basic_data import CourseType


class GradeCreate(BaseModel):
    name: str
    sort_order: int = 0


class GradeUpdate(BaseModel):
    name: Optional[str] = None
    sort_order: Optional[int] = None


class GradeInfo(BaseModel):
    id: str
    school_id: str
    semester_id: str
    name: str
    sort_order: int
    created_at: datetime

    model_config = {"from_attributes": True}


class ClassCreate(BaseModel):
    grade_id: str
    name: str
    teacher_id: Optional[str] = None
    classroom_id: Optional[str] = None
    is_teaching_class: bool = False


class ClassUpdate(BaseModel):
    name: Optional[str] = None
    teacher_id: Optional[str] = None
    classroom_id: Optional[str] = None
    is_teaching_class: Optional[bool] = None


class ClassInfo(BaseModel):
    id: str
    school_id: str
    semester_id: str
    grade_id: str
    name: str
    teacher_id: Optional[str] = None
    teacher_name: Optional[str] = None
    classroom_id: Optional[str] = None
    classroom_name: Optional[str] = None
    is_teaching_class: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class CourseCreate(BaseModel):
    code: str
    name: str
    course_type: CourseType = CourseType.REQUIRED
    weekly_hours: int = 1


class CourseUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    course_type: Optional[CourseType] = None
    weekly_hours: Optional[int] = None


class CourseInfo(BaseModel):
    id: str
    school_id: str
    code: str
    name: str
    course_type: CourseType
    weekly_hours: int
    created_at: datetime

    model_config = {"from_attributes": True}


class GradeCourseCreate(BaseModel):
    grade_id: str
    course_id: str


class GradeCourseInfo(BaseModel):
    id: str
    grade_id: str
    course_id: str
    course_name: Optional[str] = None

    model_config = {"from_attributes": True}


class TeacherCreate(BaseModel):
    name: str
    employee_id: str
    gender: str = ""
    phone: str = ""
    teaching_group: str = ""
    user_id: Optional[str] = None


class TeacherUpdate(BaseModel):
    name: Optional[str] = None
    employee_id: Optional[str] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    teaching_group: Optional[str] = None


class TeacherInfo(BaseModel):
    id: str
    school_id: str
    semester_id: str
    user_id: Optional[str] = None
    name: str
    employee_id: str
    gender: str
    phone: str
    teaching_group: str
    created_at: datetime

    model_config = {"from_attributes": True}


class TeacherCourseCreate(BaseModel):
    teacher_id: str
    course_id: str


class TeacherCourseInfo(BaseModel):
    id: str
    teacher_id: str
    course_id: str
    course_name: Optional[str] = None
    teacher_name: Optional[str] = None

    model_config = {"from_attributes": True}


class ClassroomCreate(BaseModel):
    name: str
    room_type: str = "normal"
    capacity: int = 50


class ClassroomUpdate(BaseModel):
    name: Optional[str] = None
    room_type: Optional[str] = None
    capacity: Optional[int] = None


class ClassroomInfo(BaseModel):
    id: str
    school_id: str
    semester_id: str
    name: str
    room_type: str
    capacity: int
    created_at: datetime

    model_config = {"from_attributes": True}


class ClassroomCourseCreate(BaseModel):
    classroom_id: str
    course_id: str


class ClassroomCourseInfo(BaseModel):
    id: str
    classroom_id: str
    course_id: str
    course_name: Optional[str] = None
    classroom_name: Optional[str] = None

    model_config = {"from_attributes": True}


class TeachingArrangementCreate(BaseModel):
    teacher_id: str
    course_id: str
    class_id: str
    weekly_hours: int = 1


class TeachingArrangementUpdate(BaseModel):
    weekly_hours: Optional[int] = None


class TeachingArrangementInfo(BaseModel):
    id: str
    teacher_id: str
    course_id: str
    class_id: str
    weekly_hours: int
    teacher_name: Optional[str] = None
    course_name: Optional[str] = None
    class_name: Optional[str] = None

    model_config = {"from_attributes": True}
