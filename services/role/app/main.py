from __future__ import annotations

import contextlib
from contextlib import asynccontextmanager

from fastapi import FastAPI
from hotelstaff_shared.correlation import CorrelationIdMiddleware
from hotelstaff_shared.logging import configure_logging, get_logger
from hotelstaff_shared.messaging import EventBus

from .config import settings
from .infrastructure.db.session import build_engine, build_sessionmaker
from .infrastructure.events import NullEventPublisher, RabbitMQPublisher
from .interfaces.api.health import router as health_router
from .interfaces.api.roles import router as roles_router

log = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging(
        service_name=settings.service_name,
        level=settings.log_level,
        json_output=settings.log_format == "json",
    )
    engine = build_engine(settings.postgres_dsn)
    app.state.engine = engine
    app.state.sessionmaker = build_sessionmaker(engine)
    bus: EventBus | None = None
    if settings.events_enabled:
        bus = EventBus(settings.rabbitmq_url, settings.events_exchange)
        try:
            await bus.connect()
            app.state.publisher = RabbitMQPublisher(bus)
        except Exception as exc:
            log.warning("events.unavailable", error=str(exc))
            app.state.publisher = NullEventPublisher()
            bus = None
    else:
        app.state.publisher = NullEventPublisher()
    log.info("service.startup", env=settings.service_env)
    yield
    if bus is not None:
        with contextlib.suppress(Exception):
            await bus.close()
    await engine.dispose()


app = FastAPI(
    title="HotelStaffIA — role-service",
    version="0.1.0",
    lifespan=lifespan,
)
app.add_middleware(CorrelationIdMiddleware)
app.include_router(health_router, prefix="/health", tags=["health"])
app.include_router(roles_router, tags=["roles"])
