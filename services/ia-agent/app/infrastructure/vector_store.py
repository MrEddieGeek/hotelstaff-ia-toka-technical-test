from __future__ import annotations

import math

from ..domain.entities import RetrievedChunk, StaffDocument


class QdrantVectorStore:
    def __init__(self, url: str, collection: str) -> None:
        from qdrant_client import AsyncQdrantClient

        self._client = AsyncQdrantClient(url=url)
        self._collection = collection
        self._ready = False

    async def ensure_collection(self, vector_size: int) -> None:
        if self._ready:
            return
        from qdrant_client.http import models as qm

        collections = await self._client.get_collections()
        names = {c.name for c in collections.collections}
        if self._collection not in names:
            await self._client.create_collection(
                collection_name=self._collection,
                vectors_config=qm.VectorParams(size=vector_size, distance=qm.Distance.COSINE),
            )
        self._ready = True

    async def upsert(self, docs: list[StaffDocument], vectors: list[list[float]]) -> None:
        from qdrant_client.http import models as qm

        points = [
            qm.PointStruct(
                id=d.doc_id,
                vector=v,
                payload={"text": d.text, "metadata": d.metadata},
            )
            for d, v in zip(docs, vectors, strict=True)
        ]
        await self._client.upsert(collection_name=self._collection, points=points)

    async def search(self, vector: list[float], top_k: int) -> list[RetrievedChunk]:
        results = await self._client.search(
            collection_name=self._collection, query_vector=vector, limit=top_k
        )
        return [
            RetrievedChunk(
                doc_id=str(r.id),
                text=(r.payload or {}).get("text", ""),
                score=float(r.score),
                metadata=(r.payload or {}).get("metadata", {}),
            )
            for r in results
        ]


class InMemoryVectorStore:
    """Fallback in-memory para tests — coseno sobre vectores normalizados."""

    def __init__(self) -> None:
        self._docs: dict[str, tuple[StaffDocument, list[float]]] = {}

    async def ensure_collection(self, vector_size: int) -> None:
        return

    async def upsert(self, docs: list[StaffDocument], vectors: list[list[float]]) -> None:
        for d, v in zip(docs, vectors, strict=True):
            self._docs[d.doc_id] = (d, v)

    async def search(self, vector: list[float], top_k: int) -> list[RetrievedChunk]:
        def cos(a: list[float], b: list[float]) -> float:
            return sum(x * y for x, y in zip(a, b, strict=True)) / (
                (math.sqrt(sum(x * x for x in a)) or 1.0)
                * (math.sqrt(sum(x * x for x in b)) or 1.0)
            )

        scored = [(cos(vector, v), d) for d, v in self._docs.values()]
        scored.sort(key=lambda s: s[0], reverse=True)
        return [
            RetrievedChunk(doc_id=d.doc_id, text=d.text, score=s, metadata=d.metadata)
            for s, d in scored[:top_k]
        ]
