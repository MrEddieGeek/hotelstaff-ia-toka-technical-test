from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID


@dataclass
class Role:
    id: UUID
    name: str
    description: str | None = None
    permissions: list[str] = field(default_factory=list)
    created_at: datetime | None = None


@dataclass
class UserRoleAssignment:
    user_id: UUID
    role_id: UUID
    assigned_at: datetime | None = None
