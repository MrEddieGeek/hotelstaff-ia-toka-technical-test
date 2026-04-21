from __future__ import annotations

import os

os.environ.setdefault("USE_MONGOMOCK", "true")
os.environ.setdefault("CONSUMER_ENABLED", "false")
os.environ.setdefault("LOG_FORMAT", "text")

import pytest


@pytest.fixture()
def client():
    from fastapi.testclient import TestClient

    from app.main import app

    with TestClient(app) as c:
        yield c
