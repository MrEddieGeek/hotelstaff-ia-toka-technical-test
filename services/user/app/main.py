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
from .infrastructure.security import build_verifier
from .interfaces.api.health import router as health_router
from .interfaces.api.users import router as users_router

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
    app.state.jwt_verifier = build_verifier(settings.jwt_public_key_path, settings.jwt_issuer)
    app.state.jwt_audience = settings.jwt_audience

    bus: EventBus | None = None
    if settings.events_enabled:
        bus = EventBus(settings.rabbitmq_url, settings.events_exchange)
        try:
            await bus.connect()
            app.state.publisher = RabbitMQPublisher(bus)
            log.info("events.connected", exchange=settings.events_exchange)
        except Exception as exc:
            log.warning("events.unavailable", error=str(exc))
            app.state.publisher = NullEventPublisher()
            bus = None
    else:
        app.state.publisher = NullEventPublisher()

    if settings.demo_seed:
        from .infrastructure.seed import seed_demo_users

        with contextlib.suppress(Exception):
            await seed_demo_users(app.state.sessionmaker, app.state.publisher)

    log.info("service.startup", env=settings.service_env)
    yield
    if bus is not None:
        with contextlib.suppress(Exception):
            await bus.close()
    await engine.dispose()
    log.info("service.shutdown")


app = FastAPI(
    title="HotelStaffIA — user-service",
    version="0.1.0",
    lifespan=lifespan,
)
app.add_middleware(CorrelationIdMiddleware)
app.include_router(health_router, prefix="/health", tags=["health"])
app.include_router(users_router, prefix="/users", tags=["users"])
