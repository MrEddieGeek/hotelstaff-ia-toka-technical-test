from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class CreateRoleRequest(BaseModel):
    name: str = Field(min_length=2, max_length=80, pattern=r"^[a-zA-Z][a-zA-Z0-9_\-]+$")
    description: str | None = Field(default=None, max_length=240)
    permissions: list[str] = Field(default_factory=list)


class RoleResponse(BaseModel):
    id: UUID
    name: str
    description: str | None = None
    permissions: list[str] = []
    created_at: datetime | None = None


class AssignRoleRequest(BaseModel):
    user_id: UUID
    role_id: UUID


class AssignmentResponse(BaseModel):
    user_id: UUID
    role_id: UUID
    role_name: str
    assigned_at: datetime | None = None
