from typing import List
from pydantic import BaseModel
from app.models.period import PeriodType


class PeriodConfigItem(BaseModel):
    period_type: PeriodType
    period_index: int
    start_time: str
    end_time: str


class GradePeriodSetup(BaseModel):
    grade_id: str
    periods: List[PeriodConfigItem]


class DayPeriodSetup(BaseModel):
    day_of_week: int
    period_type: PeriodType
    period_index: int
    is_available: bool


class DayPeriodBatch(BaseModel):
    grade_id: str
    configs: List[DayPeriodSetup]


class PeriodTemplateCreate(BaseModel):
    name: str
    description: str = ""
    config_data: str


class PeriodTemplateInfo(BaseModel):
    id: str
    name: str
    description: str = ""
    config_data: str
    is_system: bool = False

    model_config = {"from_attributes": True}


class GradePeriodInfo(BaseModel):
    grade_id: str
    periods: List[PeriodConfigItem]


class DayPeriodInfo(BaseModel):
    grade_id: str
    configs: List[DayPeriodSetup]
