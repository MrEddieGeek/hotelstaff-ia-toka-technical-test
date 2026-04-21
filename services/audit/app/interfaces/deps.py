from __future__ import annotations

from fastapi import Request

from ..application.services import AuditService


def get_audit_service(request: Request) -> AuditService:
    return request.app.state.audit_service
