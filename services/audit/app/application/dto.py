from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class AuditLogResponse(BaseModel):
    event_id: str
    event_type: str
    producer: str
    occurred_at: datetime
    received_at: datetime | None = None
    payload: dict[str, Any] = Field(default_factory=dict)


class AuditListResponse(BaseModel):
    items: list[AuditLogResponse]
    total: int
