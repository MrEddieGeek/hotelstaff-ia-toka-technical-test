from __future__ import annotations

import contextlib
from contextlib import asynccontextmanager

from fastapi import FastAPI
from hotelstaff_shared.correlation import CorrelationIdMiddleware
from hotelstaff_shared.logging import configure_logging, get_logger
from hotelstaff_shared.messaging import EventBus

from .application.services import AgentService
from .config import settings
from .infrastructure.consumer import UserEventIndexer
from .infrastructure.factories import build_embeddings, build_llm, build_vector_store
from .interfaces.api.agent import router as agent_router
from .interfaces.api.health import router as health_router

log = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging(
        service_name=settings.service_name,
        level=settings.log_level,
        json_output=settings.log_format == "json",
    )
    embeddings = build_embeddings(settings)
    store = build_vector_store(settings)
    llm = build_llm(settings)
    app.state.agent_service = AgentService(embeddings=embeddings, store=store, llm=llm)

    bus: EventBus | None = None
    if settings.consumer_enabled:
        bus = EventBus(settings.rabbitmq_url, settings.events_exchange)
        try:
            await bus.connect()
            indexer = UserEventIndexer(bus, app.state.agent_service, settings.events_queue)
            await indexer.start()
            app.state.event_bus = bus
        except Exception as exc:
            log.warning("consumer.unavailable", error=str(exc))
            bus = None

    log.info("service.startup", env=settings.service_env, llm=settings.llm_provider)
    yield
    if bus is not None:
        with contextlib.suppress(Exception):
            await bus.close()


app = FastAPI(
    title="HotelStaffIA — ia-agent",
    version="0.1.0",
    lifespan=lifespan,
)
app.add_middleware(CorrelationIdMiddleware)
app.include_router(health_router, prefix="/health", tags=["health"])
app.include_router(agent_router, prefix="/agent", tags=["agent"])
