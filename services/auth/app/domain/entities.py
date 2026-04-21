from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID


@dataclass
class User:
    id: UUID
    email: str
    password_hash: str
    is_active: bool = True
    created_at: datetime | None = None
    roles: list[str] = field(default_factory=list)
