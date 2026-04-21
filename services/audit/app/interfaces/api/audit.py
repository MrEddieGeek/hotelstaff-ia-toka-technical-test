from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from ...application.dto import AuditListResponse, AuditLogResponse
from ...application.services import AuditService
from ..deps import get_audit_service

router = APIRouter()


def _to_resp(log) -> AuditLogResponse:
    return AuditLogResponse(
        event_id=log.event_id,
        event_type=log.event_type,
        producer=log.producer,
        occurred_at=log.occurred_at,
        received_at=log.received_at,
        payload=log.payload,
    )


@router.get("", response_model=AuditListResponse)
async def list_audit_logs(
    event_type: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    svc: AuditService = Depends(get_audit_service),
) -> AuditListResponse:
    items, total = await svc.query(event_type=event_type, limit=limit, offset=offset)
    return AuditListResponse(items=[_to_resp(i) for i in items], total=total)
