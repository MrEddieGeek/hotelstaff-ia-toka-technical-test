from __future__ import annotations

import os

os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("JWT_PRIVATE_KEY_PATH", "/nonexistent")
os.environ.setdefault("LOG_FORMAT", "text")

import pytest

from app.infrastructure.db.models import Base

# SQLite no soporta schemas: retiramos el prefijo antes de cualquier ejecución.
for table in Base.metadata.tables.values():
    table.schema = None


@pytest.fixture()
def client():
    from fastapi.testclient import TestClient

    from app.main import app

    with TestClient(app) as c:
        import asyncio

        async def _setup():
            async with app.state.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

        asyncio.new_event_loop().run_until_complete(_setup())
        yield c
