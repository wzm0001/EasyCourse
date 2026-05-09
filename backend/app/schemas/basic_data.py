from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, field_validator
from app.models.basic_data import CourseType
from app.models.period import PeriodType


class GradeCreate(BaseModel):
    name: str
    sort_order: int = 0
    morning_reading_count: int = 1
    regular_class_count: int = 8
    evening_study_count: int = 0
    grade_leader_id: Optional[str] = None

    @field_validator("morning_reading_count")
    @classmethod
    def validate_morning_reading_count(cls, v: int) -> int:
        if not 0 <= v <= 3:
            raise ValueError("早读节数必须在0-3之间")
        return v

    @field_validator("regular_class_count")
    @classmethod
    def validate_regular_class_count(cls, v: int) -> int:
        if not 1 <= v <= 12:
            raise ValueError("正课节数必须在1-12之间")
        return v

    @field_validator("evening_study_count")
    @classmethod
    def validate_evening_study_count(cls, v: int) -> int:
        if not 0 <= v <= 4:
            raise ValueError("晚自习节数必须在0-4之间")
        return v


class GradeUpdate(BaseModel):
    name: Optional[str] = None
    sort_order: Optional[int] = None
    morning_reading_count: Optional[int] = None
    regular_class_count: Optional[int] = None
    evening_study_count: Optional[int] = None
    grade_leader_id: Optional[str] = None

    @field_validator("morning_reading_count")
    @classmethod
    def validate_morning_reading_count(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and not 0 <= v <= 3:
            raise ValueError("早读节数必须在0-3之间")
        return v

    @field_validator("regular_class_count")
    @classmethod
    def validate_regular_class_count(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and not 1 <= v <= 12:
            raise ValueError("正课节数必须在1-12之间")
        return v

    @field_validator("evening_study_count")
    @classmethod
    def validate_evening_study_count(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and not 0 <= v <= 4:
            raise ValueError("晚自习节数必须在0-4之间")
        return v


class GradeInfo(BaseModel):
    id: str
    school_id: str
    semester_id: str
    name: str
    sort_order: int
    morning_reading_count: int = 1
    regular_class_count: int = 8
    evening_study_count: int = 0
    grade_leader_id: Optional[str] = None
    grade_leader_name: Optional[str] = None
    course_count: int = 0
    created_at: datetime

    model_config = {"from_attributes": True}


class ClassCreate(BaseModel):
    grade_id: str
    name: str
    classroom_id: str
    head_teacher_id: Optional[str] = None
    is_teaching_class: bool = False


class ClassUpdate(BaseModel):
    name: Optional[str] = None
    head_teacher_id: Optional[str] = None
    classroom_id: Optional[str] = None
    is_teaching_class: Optional[bool] = None


class ClassInfo(BaseModel):
    id: str
    school_id: str
    semester_id: str
    grade_id: str
    name: str
    head_teacher_id: Optional[str] = None
    head_teacher_name: Optional[str] = None
    classroom_id: Optional[str] = None
    classroom_name: Optional[str] = None
    grade_name: Optional[str] = None
    is_teaching_class: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class CourseCreate(BaseModel):
    code: str = ""
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
    weekly_hours: int = 1
    period_type: PeriodType = PeriodType.REGULAR


class GradeCourseUpdate(BaseModel):
    weekly_hours: Optional[int] = None
    period_type: Optional[PeriodType] = None


class GradeCourseInfo(BaseModel):
    id: str
    grade_id: str
    course_id: str
    course_name: Optional[str] = None
    course_code: Optional[str] = None
    weekly_hours: int = 1
    period_type: str = "regular"

    model_config = {"from_attributes": True}


class BatchGradeCourseItem(BaseModel):
    name: str
    weekly_hours: int = 1


class BatchGradeCourseCreate(BaseModel):
    grade_id: str
    period_type: PeriodType = PeriodType.REGULAR
    courses: List[BatchGradeCourseItem]


class TeacherCreate(BaseModel):
    name: str
    phone: str
    gender: str = ""
    employee_id: str = ""
    teaching_group: str = ""
    specialization: str = ""
    email: str = ""
    user_id: Optional[str] = None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        if v and not v.startswith("1"):
            raise ValueError("手机号必须以1开头")
        if v and not v.isdigit():
            raise ValueError("手机号必须为纯数字")
        if v and len(v) != 11:
            raise ValueError("手机号必须为11位")
        return v


class TeacherUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    gender: Optional[str] = None
    employee_id: Optional[str] = None
    teaching_group: Optional[str] = None
    specialization: Optional[str] = None


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
    specialization: str
    course_names: Optional[List[str]] = None
    arrangements: Optional[List[dict]] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class TeacherCourseCreate(BaseModel):
    teacher_id: str
    course_id: str


class TeacherCourseBatchSet(BaseModel):
    course_ids: List[str]


class TeacherCourseInfo(BaseModel):
    id: str
    teacher_id: str
    course_id: str
    course_name: Optional[str] = None
    teacher_name: Optional[str] = None

    model_config = {"from_attributes": True}


class ClassroomCreate(BaseModel):
    building_name: str
    room_number: str
    room_type: str = "normal"
    capacity: int = 50


class ClassroomUpdate(BaseModel):
    building_name: Optional[str] = None
    room_number: Optional[str] = None
    room_type: Optional[str] = None
    capacity: Optional[int] = None


class ClassroomInfo(BaseModel):
    id: str
    school_id: str
    semester_id: str
    building_name: str
    room_number: str
    code: str
    room_type: str
    capacity: int
    created_at: datetime

    @property
    def display_name(self) -> str:
        return f"{self.building_name} {self.room_number}"

    model_config = {"from_attributes": True}


class ClassroomCourseCreate(BaseModel):
    classroom_id: str
    course_id: str


class ClassroomCourseBatchSet(BaseModel):
    course_ids: List[str]


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
    continuous_hours: int = 1


class TeachingArrangementUpdate(BaseModel):
    weekly_hours: Optional[int] = None
    continuous_hours: Optional[int] = None
    teacher_id: Optional[str] = None


class TeachingArrangementInfo(BaseModel):
    id: str
    teacher_id: str
    course_id: str
    class_id: str
    weekly_hours: int
    continuous_hours: int = 1
    teacher_name: Optional[str] = None
    course_name: Optional[str] = None
    class_name: Optional[str] = None
    grade_name: Optional[str] = None

    model_config = {"from_attributes": True}


class BatchTeachingArrangementCreate(BaseModel):
    grade_id: str
    arrangements: List[TeachingArrangementCreate]


class QuickSetupRequest(BaseModel):
    grade_name: str
    class_names: List[str]
    classroom_names: Optional[List[str]] = None
    morning_reading_count: int = 1
    regular_class_count: int = 8
    evening_study_count: int = 0

    @field_validator("morning_reading_count")
    @classmethod
    def validate_morning_reading_count(cls, v: int) -> int:
        if not 0 <= v <= 3:
            raise ValueError("早读节数必须在0-3之间")
        return v

    @field_validator("regular_class_count")
    @classmethod
    def validate_regular_class_count(cls, v: int) -> int:
        if not 1 <= v <= 12:
            raise ValueError("正课节数必须在1-12之间")
        return v

    @field_validator("evening_study_count")
    @classmethod
    def validate_evening_study_count(cls, v: int) -> int:
        if not 0 <= v <= 4:
            raise ValueError("晚自习节数必须在0-4之间")
        return v


class QuickSetupResult(BaseModel):
    grade_id: str
    class_ids: List[str]
    classroom_ids: List[str]


class TeachingArrangementSummary(BaseModel):
    class_id: str
    class_name: str
    grade_id: str
    grade_name: str
    classroom_name: Optional[str] = None
    total_courses: int = 0
    assigned_count: int = 0
    courses: List[GradeCourseInfo]
    teacher_assignments: List[TeachingArrangementInfo]
