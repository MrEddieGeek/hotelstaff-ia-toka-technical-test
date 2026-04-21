from __future__ import annotations

from typing import Protocol

from ..domain.entities import RetrievedChunk, StaffDocument


class EmbeddingProvider(Protocol):
    async def embed(self, texts: list[str]) -> list[list[float]]: ...


class VectorStore(Protocol):
    async def ensure_collection(self, vector_size: int) -> None: ...

    async def upsert(self, docs: list[StaffDocument], vectors: list[list[float]]) -> None: ...

    async def search(self, vector: list[float], top_k: int) -> list[RetrievedChunk]: ...


class LLMProvider(Protocol):
    async def complete(self, *, system: str, user: str) -> str: ...
