"""Publisher y consumer de RabbitMQ basados en aio-pika (async).

Los servicios usan ``EventBus.publish(event)`` para emitir eventos de dominio
y ``EventBus.consume(routing_keys, handler)`` para suscribirse a ellos.
"""

from __future__ import annotations

import json
from collections.abc import Awaitable, Callable

import aio_pika
from aio_pika.abc import AbstractIncomingMessage

from .events import DomainEvent
from .logging import get_logger

log = get_logger(__name__)
EventHandler = Callable[[DomainEvent], Awaitable[None]]


class EventBus:
    def __init__(self, url: str, exchange_name: str) -> None:
        self._url = url
        self._exchange_name = exchange_name
        self._connection: aio_pika.abc.AbstractRobustConnection | None = None
        self._channel: aio_pika.abc.AbstractRobustChannel | None = None
        self._exchange: aio_pika.abc.AbstractExchange | None = None

    async def connect(self) -> None:
        self._connection = await aio_pika.connect_robust(self._url)
        self._channel = await self._connection.channel()
        await self._channel.set_qos(prefetch_count=16)
        self._exchange = await self._channel.declare_exchange(
            self._exchange_name, aio_pika.ExchangeType.TOPIC, durable=True
        )

    async def close(self) -> None:
        if self._connection is not None:
            await self._connection.close()

    async def publish(self, event: DomainEvent) -> None:
        if self._exchange is None:
            raise RuntimeError("EventBus no conectado; llama a connect() primero")
        message = aio_pika.Message(
            body=event.model_dump_json().encode("utf-8"),
            content_type="application/json",
            message_id=event.event_id,
            headers={"producer": event.producer, "version": event.version},
        )
        await self._exchange.publish(message, routing_key=event.event_type)
        log.info("event.published", event_type=event.event_type, event_id=event.event_id)

    async def consume(
        self,
        queue_name: str,
        routing_keys: list[str],
        handler: EventHandler,
    ) -> None:
        if self._channel is None or self._exchange is None:
            raise RuntimeError("EventBus no conectado; llama a connect() primero")
        queue = await self._channel.declare_queue(
            queue_name,
            durable=True,
            arguments={"x-dead-letter-exchange": f"{self._exchange_name}.dlx"},
        )
        for rk in routing_keys:
            await queue.bind(self._exchange, routing_key=rk)

        async def _on_message(message: AbstractIncomingMessage) -> None:
            async with message.process(requeue=False):
                try:
                    data = json.loads(message.body.decode("utf-8"))
                    event = DomainEvent.model_validate(data)
                    await handler(event)
                    log.info("event.processed", event_type=event.event_type, event_id=event.event_id)
                except Exception as exc:  # noqa: BLE001
                    log.exception("event.failed", error=str(exc))
                    raise

        await queue.consume(_on_message)
