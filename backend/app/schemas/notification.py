from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from app.models.notification import NotificationType


class NotificationCreate(BaseModel):
    type: NotificationType
    title: str
    content: str
    receiver_id: str
    school_id: Optional[str] = None


class NotificationInfo(BaseModel):
    id: str
    school_id: Optional[str] = None
    type: NotificationType
    title: str
    content: str
    sender_id: Optional[str] = None
    receiver_id: str
    is_read: bool = False
    created_at: datetime

    model_config = {"from_attributes": True}


class NotificationBatchCreate(BaseModel):
    type: NotificationType
    title: str
    content: str
    receiver_ids: List[str]
    school_id: Optional[str] = None
