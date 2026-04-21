from __future__ import annotations

import contextlib
from contextlib import asynccontextmanager

from fastapi import FastAPI
from hotelstaff_shared.correlation import CorrelationIdMiddleware
from hotelstaff_shared.logging import configure_logging, get_logger

from .application.services import AuthService
from .config import settings
from .domain.errors import EmailAlreadyRegistered
from .infrastructure.db.session import build_engine, build_sessionmaker
from .infrastructure.repositories import SqlAlchemyUserRepository
from .infrastructure.security.jwt_service import RS256TokenService
from .infrastructure.security.password import Argon2PasswordHasher
from .interfaces.api.auth import router as auth_router
from .interfaces.api.health import router as health_router
from .interfaces.api.jwks import router as jwks_router
from .interfaces.deps import load_or_generate_private_key

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
    app.state.hasher = Argon2PasswordHasher()
    app.state.tokens = RS256TokenService(
        private_key_pem=load_or_generate_private_key(settings.jwt_private_key_path),
        issuer=settings.jwt_issuer,
        audience=settings.jwt_audience,
        access_ttl_seconds=settings.jwt_access_ttl_seconds,
        refresh_ttl_seconds=settings.jwt_refresh_ttl_seconds,
    )
    if settings.demo_seed:
        with contextlib.suppress(Exception):
            async with app.state.sessionmaker() as session:
                svc = AuthService(
                    users=SqlAlchemyUserRepository(session),
                    hasher=app.state.hasher,
                    tokens=app.state.tokens,
                )
                try:
                    await svc.register(settings.demo_email, settings.demo_password)
                    await session.commit()
                    log.info("demo.admin.seeded", email=settings.demo_email)
                except EmailAlreadyRegistered:
                    log.info("demo.admin.exists", email=settings.demo_email)

    log.info("service.startup", env=settings.service_env)
    yield
    await engine.dispose()
    log.info("service.shutdown")


app = FastAPI(
    title="HotelStaffIA — auth-service",
    version="0.1.0",
    lifespan=lifespan,
)
app.add_middleware(CorrelationIdMiddleware)
app.include_router(health_router, prefix="/health", tags=["health"])
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(jwks_router, prefix="/.well-known", tags=["jwks"])
