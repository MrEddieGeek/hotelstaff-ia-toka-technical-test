from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class CreateUserRequest(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=1, max_length=200)
    position: str = Field(min_length=1, max_length=120)
    department: str | None = Field(default=None, max_length=120)


class UpdateUserRequest(BaseModel):
    full_name: str | None = Field(default=None, min_length=1, max_length=200)
    position: str | None = Field(default=None, min_length=1, max_length=120)
    department: str | None = Field(default=None, max_length=120)
    is_active: bool | None = None


class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    full_name: str
    position: str
    department: str | None = None
    is_active: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None


class UserListResponse(BaseModel):
    items: list[UserResponse]
    total: int
