from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from app.models.user import UserRole, AccountStatus


class LoginRequest(BaseModel):
    username: str
    password: str


class UserInfo(BaseModel):
    id: str
    username: str
    real_name: str = ""
    role: UserRole
    school_id: Optional[str] = None
    school_name: Optional[str] = None
    phone: str = ""
    email: str = ""
    is_active: bool = True

    model_config = {"from_attributes": True}


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserInfo


class SchoolCreate(BaseModel):
    name: str
    code: str
    address: str = ""
    contact_person: str = ""
    contact_phone: str = ""


class SchoolUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    contact_person: Optional[str] = None
    contact_phone: Optional[str] = None


class SchoolInfo(BaseModel):
    id: str
    name: str
    code: str
    address: str = ""
    contact_person: str = ""
    contact_phone: str = ""
    status: AccountStatus
    created_at: datetime

    model_config = {"from_attributes": True}


class UserCreate(BaseModel):
    username: str
    password: str
    real_name: str = ""
    role: UserRole
    school_id: Optional[str] = None
    phone: str = ""
    email: str = ""


class UserUpdate(BaseModel):
    real_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None


class TeacherCreate(BaseModel):
    username: str
    password: str
    real_name: str = ""
    phone: str = ""
    email: str = ""


class ApprovalInfo(BaseModel):
    id: str
    type: str
    requester_id: str
    school_id: Optional[str] = None
    status: str = "pending"
    request_data: str = ""
    reject_reason: str = ""
    reviewer_id: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ApprovalAction(BaseModel):
    status: str = Field(pattern=r"^(approved|rejected)$")
    reject_reason: Optional[str] = None


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


class UserStatusUpdate(BaseModel):
    is_active: bool


class ResetPasswordRequest(BaseModel):
    username: str
    new_password: str


class VerifyIdentityRequest(BaseModel):
    username: str
    phone: str
