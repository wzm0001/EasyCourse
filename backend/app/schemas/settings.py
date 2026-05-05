from typing import Optional
from pydantic import BaseModel


class SettingUpdate(BaseModel):
    key: str
    value: str


class SettingInfo(BaseModel):
    id: str
    key: str
    value: str
    description: str = ""
    is_public: bool = False

    model_config = {"from_attributes": True}


class DatabaseSwitchRequest(BaseModel):
    database_type: str
    mysql_host: Optional[str] = None
    mysql_port: Optional[int] = None
    mysql_user: Optional[str] = None
    mysql_password: Optional[str] = None
    mysql_database: Optional[str] = None


class DatabaseTestResult(BaseModel):
    success: bool
    message: str


class PasswordPolicyConfig(BaseModel):
    min_length: int = 8
    require_uppercase: bool = True
    require_lowercase: bool = True
    require_digit: bool = True
    require_special: bool = False


class SystemSettingsInfo(BaseModel):
    database_type: str
    password_policy: PasswordPolicyConfig
    token_expire_minutes: int
    maintenance_mode: bool
    auto_backup_enabled: bool
    auto_backup_cron: str
