from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel


class SemesterCreate(BaseModel):
    name: str
    start_date: str
    end_date: str
    total_weeks: int = 20
    description: str = ""


class SemesterUpdate(BaseModel):
    name: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    total_weeks: Optional[int] = None
    description: Optional[str] = None


class SemesterInfo(BaseModel):
    id: str
    school_id: str
    name: str
    start_date: str
    end_date: str
    total_weeks: int
    is_active: bool
    is_archived: bool
    description: str
    created_at: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm(cls, obj):
        return cls(
            id=obj.id,
            school_id=obj.school_id,
            name=obj.name,
            start_date=obj.start_date.isoformat() if isinstance(obj.start_date, date) else str(obj.start_date),
            end_date=obj.end_date.isoformat() if isinstance(obj.end_date, date) else str(obj.end_date),
            total_weeks=obj.total_weeks,
            is_active=obj.is_active,
            is_archived=obj.is_archived,
            description=obj.description,
            created_at=obj.created_at,
        )


class SemesterCopyRequest(BaseModel):
    target_semester_id: str
