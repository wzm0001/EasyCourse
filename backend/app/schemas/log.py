from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.models.log import LogType, LogLevel


class LogQuery(BaseModel):
    log_type: Optional[LogType] = None
    level: Optional[LogLevel] = None
    user_id: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    keyword: Optional[str] = None
    page: int = 1
    page_size: int = 20


class LogInfo(BaseModel):
    id: str
    log_type: LogType
    level: LogLevel
    user_id: Optional[str] = None
    username: str = ""
    school_id: Optional[str] = None
    action: str
    target_type: str = ""
    target_id: str = ""
    detail: str = ""
    ip_address: str = ""
    stack_trace: str = ""
    created_at: datetime

    model_config = {"from_attributes": True}
