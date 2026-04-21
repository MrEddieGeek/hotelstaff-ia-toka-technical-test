from __future__ import annotations

import asyncio

from hotelstaff_shared.events import DomainEvent
from hotelstaff_shared.logging import get_logger
from hotelstaff_shared.messaging import EventBus

from ..application.services import AuditService

log = get_logger(__name__)
ROUTING_KEYS = [
    "user.*",
    "auth.*",
    "role.*",
]


class AuditConsumer:
    def __init__(self, bus: EventBus, service: AuditService, queue_name: str) -> None:
        self._bus = bus
        self._service = service
        self._queue_name = queue_name
        self._task: asyncio.Task | None = None

    async def start(self) -> None:
        async def handler(event: DomainEvent) -> None:
            await self._service.record(event)

        self._task = asyncio.create_task(self._bus.consume(self._queue_name, ROUTING_KEYS, handler))
        log.info("audit.consumer.started", queue=self._queue_name, keys=ROUTING_KEYS)
