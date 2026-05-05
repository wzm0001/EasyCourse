from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from app.models.constraint import ConstraintType, ConstraintPriority


class ConstraintCreate(BaseModel):
    constraint_type: ConstraintType
    priority: ConstraintPriority = ConstraintPriority.MEDIUM
    is_active: bool = True
    teacher_id: Optional[str] = None
    course_id: Optional[str] = None
    classroom_id: Optional[str] = None
    grade_id: Optional[str] = None
    day_of_week: Optional[int] = None
    period_type: Optional[str] = None
    period_index: Optional[int] = None
    max_daily_hours: Optional[int] = None
    allow_continuous: Optional[bool] = None
    require_scatter: Optional[bool] = None
    description: str = ""


class ConstraintUpdate(BaseModel):
    priority: Optional[ConstraintPriority] = None
    is_active: Optional[bool] = None
    day_of_week: Optional[int] = None
    period_type: Optional[str] = None
    period_index: Optional[int] = None
    max_daily_hours: Optional[int] = None
    allow_continuous: Optional[bool] = None
    require_scatter: Optional[bool] = None
    description: Optional[str] = None


class ConstraintInfo(BaseModel):
    id: str
    school_id: str
    semester_id: str
    constraint_type: ConstraintType
    priority: ConstraintPriority
    is_active: bool
    teacher_id: Optional[str] = None
    teacher_name: Optional[str] = None
    course_id: Optional[str] = None
    course_name: Optional[str] = None
    classroom_id: Optional[str] = None
    classroom_name: Optional[str] = None
    grade_id: Optional[str] = None
    grade_name: Optional[str] = None
    day_of_week: Optional[int] = None
    period_type: Optional[str] = None
    period_index: Optional[int] = None
    max_daily_hours: Optional[int] = None
    allow_continuous: Optional[bool] = None
    require_scatter: Optional[bool] = None
    description: str = ""
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
