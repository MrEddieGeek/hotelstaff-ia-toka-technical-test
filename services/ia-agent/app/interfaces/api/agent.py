from __future__ import annotations

from fastapi import APIRouter, Depends, status

from ...application.dto import (
    AskRequest,
    AskResponse,
    IndexDocumentRequest,
    SourceChunk,
)
from ...application.services import AgentService
from ..deps import get_agent_service

router = APIRouter()


@router.post("/index", status_code=status.HTTP_202_ACCEPTED)
async def index_doc(
    payload: IndexDocumentRequest,
    svc: AgentService = Depends(get_agent_service),
) -> dict:
    await svc.index(payload)
    return {"status": "indexed", "doc_id": payload.doc_id}


@router.post("/index/bulk", status_code=status.HTTP_202_ACCEPTED)
async def index_bulk(
    docs: list[IndexDocumentRequest],
    svc: AgentService = Depends(get_agent_service),
) -> dict:
    n = await svc.index_many(docs)
    return {"status": "indexed", "count": n}


@router.post("/ask", response_model=AskResponse)
async def ask(
    payload: AskRequest,
    svc: AgentService = Depends(get_agent_service),
) -> AskResponse:
    result = await svc.ask(payload)
    return AskResponse(
        answer=result.answer,
        sources=[
            SourceChunk(doc_id=c.doc_id, text=c.text, score=c.score, metadata=c.metadata)
            for c in result.sources
        ],
    )
