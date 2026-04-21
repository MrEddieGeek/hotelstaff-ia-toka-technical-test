from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class StaffDocument:
    """Documento que describe a un staff, indexado en la base vectorial."""

    doc_id: str
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class RetrievedChunk:
    doc_id: str
    text: str
    score: float
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentAnswer:
    answer: str
    sources: list[RetrievedChunk] = field(default_factory=list)
