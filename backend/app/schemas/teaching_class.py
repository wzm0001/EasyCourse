from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class TeachingClassCreate(BaseModel):
    grade_id: str
    name: str
    course_id: str
    teacher_id: str
    classroom_id: Optional[str] = None
    description: Optional[str] = ""
    member_class_ids: List[str] = []


class TeachingClassUpdate(BaseModel):
    name: Optional[str] = None
    teacher_id: Optional[str] = None
    classroom_id: Optional[str] = None
    description: Optional[str] = None
    member_class_ids: Optional[List[str]] = None


class TeachingClassMemberInfo(BaseModel):
    id: str
    teaching_class_id: str
    class_id: str
    class_name: Optional[str] = None

    model_config = {"from_attributes": True}


class TeachingClassInfo(BaseModel):
    id: str
    school_id: str
    semester_id: str
    grade_id: str
    name: str
    course_id: str
    course_name: Optional[str] = None
    teacher_id: str
    teacher_name: Optional[str] = None
    classroom_id: Optional[str] = None
    classroom_name: Optional[str] = None
    description: str
    members: List[TeachingClassMemberInfo] = []
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
