from __future__ import annotations

import os

os.environ.setdefault("USE_MEMORY_VECTOR_STORE", "true")
os.environ.setdefault("LLM_PROVIDER", "stub")
os.environ.setdefault("CONSUMER_ENABLED", "false")
os.environ.setdefault("LOG_FORMAT", "text")
os.environ.setdefault("SERVICE_ENV", "test")

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture()
def client():
    with TestClient(app) as c:
        yield c
