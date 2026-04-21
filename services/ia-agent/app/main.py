from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from hotelstaff_shared.correlation import CorrelationIdMiddleware
from hotelstaff_shared.logging import configure_logging, get_logger

from .config import settings
from .interfaces.api.health import router as health_router

log = get_logger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    configure_logging(
        service_name=settings.service_name,
        level=settings.log_level,
        json_output=settings.log_format == "json",
    )
    log.info("service.startup", env=settings.service_env)
    yield
    log.info("service.shutdown")


app = FastAPI(
    title="HotelStaffIA — ia-agent",
    version="0.1.0",
    lifespan=lifespan,
)
app.add_middleware(CorrelationIdMiddleware)
app.include_router(health_router, prefix="/health", tags=["health"])
