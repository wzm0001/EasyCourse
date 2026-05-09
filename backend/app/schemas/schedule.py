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
    is_locked: bool = False


class ScheduleCellUpdate(BaseModel):
    course_id: Optional[str] = None
    teacher_id: Optional[str] = None
    classroom_id: Optional[str] = None
    is_locked: Optional[bool] = None


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
    class_name: Optional[str] = None
    is_locked: bool
    has_conflict: bool = False
    conflict_reasons: List[str] = []

    model_config = {"from_attributes": True}


class DragDropRequest(BaseModel):
    teacher_id: str
    course_id: Optional[str] = None
    target_class_id: str
    target_day_of_week: int
    target_period_type: str
    target_period_index: int


class CellMoveRequest(BaseModel):
    cell_id: str
    target_day_of_week: int
    target_period_type: str
    target_period_index: int


class ConflictCheckRequest(BaseModel):
    teacher_id: Optional[str] = None
    classroom_id: Optional[str] = None
    class_id: Optional[str] = None
    day_of_week: int
    period_type: str
    period_index: int
    exclude_cell_id: Optional[str] = None


class ScheduleGrid(BaseModel):
    class_id: str
    class_name: Optional[str] = None
    cells: List[ScheduleCellInfo]
    conflicts: List[ConflictInfo] = []


class ConflictInfo(BaseModel):
    type: str
    cell_id: Optional[str] = None
    conflicting_with: Optional[str] = None
    message: str


class AutoScheduleRequest(BaseModel):
    semester_id: str
    grade_id: Optional[str] = None
    keep_locked: bool = True


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
    keep_locked: bool = True
