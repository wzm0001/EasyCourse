from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class ScheduleCellCreate(BaseModel):
    class_id: str
    day_of_week: int
    period_type: str
    period_index: int
    course_id: Optional[str] = None
    teacher_id: Optional[str] = None
    classroom_id: Optional[str] = None
    is_fixed: bool = False


class ScheduleCellUpdate(BaseModel):
    course_id: Optional[str] = None
    teacher_id: Optional[str] = None
    classroom_id: Optional[str] = None
    is_fixed: Optional[bool] = None


class ScheduleCellInfo(BaseModel):
    id: str
    school_id: str
    semester_id: str
    grade_id: str
    class_id: str
    day_of_week: int
    period_type: str
    period_index: int
    course_id: Optional[str] = None
    course_name: Optional[str] = None
    teacher_id: Optional[str] = None
    teacher_name: Optional[str] = None
    classroom_id: Optional[str] = None
    classroom_name: Optional[str] = None
    is_fixed: bool

    model_config = {"from_attributes": True}


class ScheduleGrid(BaseModel):
    class_id: str
    class_name: Optional[str] = None
    cells: List[ScheduleCellInfo]


class ConflictInfo(BaseModel):
    type: str
    cell_id: Optional[str] = None
    conflicting_with: Optional[str] = None
    message: str


class AutoScheduleRequest(BaseModel):
    semester_id: str
    grade_id: Optional[str] = None


class AutoScheduleResult(BaseModel):
    total_tasks: int
    scheduled: int
    failed: int
    conflicts: List[ConflictInfo]


class SwapRequest(BaseModel):
    cell_id_1: str
    cell_id_2: str


class ScheduleLockInfo(BaseModel):
    id: str
    school_id: str
    semester_id: str
    user_id: str
    user_name: Optional[str] = None
    locked_at: str

    model_config = {"from_attributes": True}


class ClearScheduleRequest(BaseModel):
    semester_id: str
    grade_id: Optional[str] = None
