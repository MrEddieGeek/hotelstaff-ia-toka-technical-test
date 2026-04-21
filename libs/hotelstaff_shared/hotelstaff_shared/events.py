"""Contratos de eventos de dominio compartidos entre microservicios.

Todos los eventos heredan de DomainEvent. El event_id se usa como clave
de idempotencia en los consumers.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field


class DomainEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    producer: str
    version: int = 1
    payload: dict[str, Any]


# Eventos conocidos del sistema. Usar los event_type como routing keys.
USER_CREATED = "user.created"
USER_UPDATED = "user.updated"
USER_DELETED = "user.deleted"
USER_LOGGED_IN = "auth.user_logged_in"
USER_LOGIN_FAILED = "auth.user_login_failed"
ROLE_ASSIGNED = "role.assigned"
ROLE_REVOKED = "role.revoked"
