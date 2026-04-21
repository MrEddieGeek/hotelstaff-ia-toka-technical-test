from __future__ import annotations

import contextlib
from contextlib import asynccontextmanager

from fastapi import FastAPI
from hotelstaff_shared.correlation import CorrelationIdMiddleware
from hotelstaff_shared.logging import configure_logging, get_logger
from hotelstaff_shared.messaging import EventBus

from .application.services import AuditService
from .config import settings
from .infrastructure.consumer import AuditConsumer
from .infrastructure.db import build_mongo_client
from .infrastructure.repository import MongoAuditRepository
from .interfaces.api.audit import router as audit_router
from .interfaces.api.health import router as health_router

log = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging(
        service_name=settings.service_name,
        level=settings.log_level,
        json_output=settings.log_format == "json",
    )
    client = build_mongo_client(settings.mongo_uri, settings.use_mongomock)
    db = client[settings.mongo_db]
    repo = MongoAuditRepository(db)
    with contextlib.suppress(Exception):
        await repo.ensure_indexes()
    app.state.mongo_client = client
    app.state.audit_service = AuditService(repo)

    bus: EventBus | None = None
    if settings.consumer_enabled:
        bus = EventBus(settings.rabbitmq_url, settings.events_exchange)
        try:
            await bus.connect()
            consumer = AuditConsumer(bus, app.state.audit_service, settings.events_queue)
            await consumer.start()
            app.state.event_bus = bus
        except Exception as exc:
            log.warning("consumer.unavailable", error=str(exc))
            bus = None

    log.info("service.startup", env=settings.service_env)
    yield
    if bus is not None:
        with contextlib.suppress(Exception):
            await bus.close()
    client.close()


app = FastAPI(
    title="HotelStaffIA — audit-service",
    version="0.1.0",
    lifespan=lifespan,
)
app.add_middleware(CorrelationIdMiddleware)
app.include_router(health_router, prefix="/health", tags=["health"])
app.include_router(audit_router, prefix="/audit", tags=["audit"])
