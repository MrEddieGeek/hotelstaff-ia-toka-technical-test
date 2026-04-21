from __future__ import annotations

from ..application.services import AuditRepository
from ..domain.entities import AuditLog

COLLECTION = "audit_logs"


class MongoAuditRepository(AuditRepository):
    def __init__(self, db) -> None:
        self._collection = db[COLLECTION]

    async def ensure_indexes(self) -> None:
        await self._collection.create_index("event_id", unique=True)
        await self._collection.create_index("event_type")
        await self._collection.create_index([("occurred_at", -1)])

    async def insert(self, log: AuditLog) -> None:
        await self._collection.insert_one(
            {
                "event_id": log.event_id,
                "event_type": log.event_type,
                "producer": log.producer,
                "occurred_at": log.occurred_at,
                "received_at": log.received_at,
                "payload": log.payload,
            }
        )

    async def find_by_event_id(self, event_id: str) -> AuditLog | None:
        doc = await self._collection.find_one({"event_id": event_id})
        return _to_entity(doc) if doc else None

    async def find(
        self,
        *,
        event_type: str | None,
        limit: int,
        offset: int,
    ) -> tuple[list[AuditLog], int]:
        query: dict = {}
        if event_type:
            query["event_type"] = event_type
        total = await self._collection.count_documents(query)
        cursor = self._collection.find(query).sort("occurred_at", -1).skip(offset).limit(limit)
        items = [_to_entity(doc) async for doc in cursor]
        return items, int(total)


def _to_entity(doc: dict) -> AuditLog:
    return AuditLog(
        event_id=doc["event_id"],
        event_type=doc["event_type"],
        producer=doc["producer"],
        occurred_at=doc["occurred_at"],
        payload=doc.get("payload", {}),
        received_at=doc.get("received_at"),
    )
