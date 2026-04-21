from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class StaffUser:
    id: UUID
    email: str
    full_name: str
    position: str
    department: str | None = None
    is_active: bool = True
    created_at: datetime | None = None
    updated_at: datetime | None = None
