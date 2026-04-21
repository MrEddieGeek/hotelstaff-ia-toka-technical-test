from __future__ import annotations

import asyncio

from hotelstaff_shared.events import USER_CREATED, USER_UPDATED, DomainEvent
from hotelstaff_shared.logging import get_logger
from hotelstaff_shared.messaging import EventBus

from ..application.dto import IndexDocumentRequest
from ..application.services import AgentService

log = get_logger(__name__)


class UserEventIndexer:
    """Al recibir user.created/updated, indexa el staff en la base vectorial."""

    def __init__(self, bus: EventBus, service: AgentService, queue_name: str) -> None:
        self._bus = bus
        self._service = service
        self._queue_name = queue_name
        self._task: asyncio.Task | None = None

    async def start(self) -> None:
        async def handler(event: DomainEvent) -> None:
            p = event.payload
            text = " | ".join(
                str(v) for v in [p.get("full_name"), p.get("position"), p.get("department")] if v
            )
            if not text:
                return
            await self._service.index(
                IndexDocumentRequest(
                    doc_id=str(p.get("user_id") or event.event_id),
                    text=text,
                    metadata={"source_event": event.event_type, **p},
                )
            )

        self._task = asyncio.create_task(
            self._bus.consume(self._queue_name, [USER_CREATED, USER_UPDATED], handler)
        )
        log.info("ia-agent.consumer.started", queue=self._queue_name)
