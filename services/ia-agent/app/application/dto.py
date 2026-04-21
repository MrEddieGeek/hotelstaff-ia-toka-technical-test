from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class IndexDocumentRequest(BaseModel):
    doc_id: str = Field(min_length=1)
    text: str = Field(min_length=1, max_length=4000)
    metadata: dict[str, Any] = Field(default_factory=dict)


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    top_k: int = Field(default=4, ge=1, le=20)


class SourceChunk(BaseModel):
    doc_id: str
    text: str
    score: float
    metadata: dict[str, Any] = Field(default_factory=dict)


class AskResponse(BaseModel):
    answer: str
    sources: list[SourceChunk] = Field(default_factory=list)
