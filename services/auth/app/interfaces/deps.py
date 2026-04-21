from __future__ import annotations

from collections.abc import AsyncIterator
from pathlib import Path

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from ..application.services import AuthService
from ..config import Settings, settings
from ..infrastructure.repositories import SqlAlchemyUserRepository
from ..infrastructure.security.jwt_service import RS256TokenService
from ..infrastructure.security.password import Argon2PasswordHasher


def get_settings() -> Settings:
    return settings


async def get_session(request: Request) -> AsyncIterator[AsyncSession]:
    sm = request.app.state.sessionmaker
    async with sm() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


def get_token_service(request: Request) -> RS256TokenService:
    return request.app.state.tokens


def get_password_hasher(request: Request) -> Argon2PasswordHasher:
    return request.app.state.hasher


def get_auth_service(
    session: AsyncSession = Depends(get_session),
    tokens: RS256TokenService = Depends(get_token_service),
    hasher: Argon2PasswordHasher = Depends(get_password_hasher),
) -> AuthService:
    return AuthService(
        users=SqlAlchemyUserRepository(session),
        hasher=hasher,
        tokens=tokens,
    )


def load_or_generate_private_key(path: str) -> str:
    """Carga la clave privada; si no existe (dev), genera una efímera en memoria."""
    p = Path(path)
    if p.exists():
        return p.read_text(encoding="utf-8")
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import rsa

    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    return key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode("utf-8")
