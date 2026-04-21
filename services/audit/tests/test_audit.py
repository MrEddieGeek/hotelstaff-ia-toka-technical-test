from __future__ import annotations

from datetime import UTC, datetime

import pytest
from hotelstaff_shared.events import DomainEvent


@pytest.mark.asyncio
async def test_record_event_then_query(client) -> None:
    svc = client.app.state.audit_service
    event = DomainEvent(
        event_type="user.created",
        producer="user-service",
        payload={"user_id": "u-1", "email": "a@b.com"},
    )
    await svc.record(event)
    # Idempotente: segunda inserción no duplica.
    await svc.record(event)

    r = client.get("/audit")
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 1
    assert body["items"][0]["event_type"] == "user.created"
    assert body["items"][0]["payload"]["email"] == "a@b.com"


@pytest.mark.asyncio
async def test_query_filter_by_event_type(client) -> None:
    svc = client.app.state.audit_service
    for i, etype in enumerate(["user.created", "user.updated", "role.assigned"]):
        await svc.record(
            DomainEvent(
                event_type=etype,
                producer="test",
                occurred_at=datetime.now(UTC),
                payload={"i": i},
            )
        )
    r = client.get("/audit?event_type=user.created")
    assert r.status_code == 200
    assert r.json()["total"] == 1


@pytest.mark.asyncio
async def test_record_raw_event(client) -> None:
    svc = client.app.state.audit_service
    await svc.record_raw(
        event_id="evt-123",
        event_type="custom",
        producer="test",
        payload={"k": "v"},
    )
    r = client.get("/audit")
    assert r.json()["total"] == 1
    # Idempotencia también en record_raw.
    await svc.record_raw(
        event_id="evt-123",
        event_type="custom",
        producer="test",
        payload={"k": "v"},
    )
    assert client.get("/audit").json()["total"] == 1
