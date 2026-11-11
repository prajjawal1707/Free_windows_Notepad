from datetime import datetime
from typing import Dict, Optional

from pydantic import BaseModel, ConfigDict, Field

USERNAME = r"^[A-Za-z0-9_.-]+$"


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=64, pattern=USERNAME)
    password: str = Field(min_length=6, max_length=128)
    full_name: str = Field(default="", max_length=128)
    role: str = Field(default="user", pattern=r"^(admin|user)$")


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    full_name: str
    role: str
    created_at: datetime


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=64, pattern=USERNAME)
    password: str = Field(min_length=6, max_length=128)
    full_name: str = Field(default="", max_length=128)


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    token: str
    user: UserOut


class AuthStatus(BaseModel):
    has_users: bool


class SettingsPayload(BaseModel):
    values: Dict[str, str]


class DashboardStats(BaseModel):
    total_users: int
    admins: int
    active_sessions: int
    my_notes: int = 0
    server_time: datetime
    version: str
    database_path: str


class NoteIn(BaseModel):
    title: str = Field(default="", max_length=200)
    content: str = Field(default="", max_length=200000)
    tags: str = Field(default="", max_length=256)
    pinned: bool = False


class NoteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    content: str
    tags: str
    pinned: bool
    created_at: datetime
    updated_at: datetime


class ImportRequest(BaseModel):
    csv: str = Field(max_length=20_000_000)


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(default=None, max_length=128)
    role: Optional[str] = Field(default=None, pattern=r"^(admin|user)$")


class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(min_length=6, max_length=128)


class PasswordReset(BaseModel):
    new_password: str = Field(min_length=6, max_length=128)
