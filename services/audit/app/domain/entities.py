from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class AuditLog:
    event_id: str
    event_type: str
    producer: str
    occurred_at: datetime
    payload: dict[str, Any] = field(default_factory=dict)
    received_at: datetime | None = None
