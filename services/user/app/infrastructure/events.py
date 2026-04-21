from __future__ import annotations

from hotelstaff_shared.events import DomainEvent
from hotelstaff_shared.logging import get_logger
from hotelstaff_shared.messaging import EventBus

log = get_logger(__name__)


class RabbitMQPublisher:
    """Adapter del puerto EventPublisher → aio-pika."""

    def __init__(self, bus: EventBus) -> None:
        self._bus = bus

    async def publish(self, event: DomainEvent) -> None:
        await self._bus.publish(event)


class NullEventPublisher:
    """Fallback para tests o entornos sin RabbitMQ. Registra sin publicar."""

    def __init__(self) -> None:
        self.published: list[DomainEvent] = []

    async def publish(self, event: DomainEvent) -> None:
        self.published.append(event)
        log.info("event.captured", event_type=event.event_type, event_id=event.event_id)
