from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Protocol

from hotelstaff_shared.events import DomainEvent

from ..domain.entities import AuditLog


class AuditRepository(Protocol):
    async def insert(self, log: AuditLog) -> None: ...

    async def find(
        self,
        *,
        event_type: str | None,
        limit: int,
        offset: int,
    ) -> tuple[list[AuditLog], int]: ...

    async def find_by_event_id(self, event_id: str) -> AuditLog | None: ...


class AuditService:
    def __init__(self, repo: AuditRepository) -> None:
        self._repo = repo

    async def record(self, event: DomainEvent) -> None:
        # Idempotencia: si el event_id ya existe, no lo volvemos a insertar.
        if await self._repo.find_by_event_id(event.event_id):
            return
        await self._repo.insert(
            AuditLog(
                event_id=event.event_id,
                event_type=event.event_type,
                producer=event.producer,
                occurred_at=event.occurred_at,
                payload=event.payload,
                received_at=datetime.now(UTC),
            )
        )

    async def record_raw(
        self,
        *,
        event_id: str,
        event_type: str,
        producer: str,
        payload: dict[str, Any],
    ) -> None:
        now = datetime.now(UTC)
        if await self._repo.find_by_event_id(event_id):
            return
        await self._repo.insert(
            AuditLog(
                event_id=event_id,
                event_type=event_type,
                producer=producer,
                occurred_at=now,
                payload=payload,
                received_at=now,
            )
        )

    async def query(
        self,
        *,
        event_type: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[AuditLog], int]:
        return await self._repo.find(event_type=event_type, limit=limit, offset=offset)
