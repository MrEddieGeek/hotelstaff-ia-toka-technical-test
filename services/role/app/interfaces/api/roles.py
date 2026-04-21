from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from ...application.dto import (
    AssignmentResponse,
    AssignRoleRequest,
    CreateRoleRequest,
    RoleResponse,
)
from ...application.services import RoleService
from ...domain.errors import (
    AssignmentAlreadyExists,
    AssignmentNotFound,
    RoleAlreadyExists,
    RoleNotFound,
)
from ..deps import get_role_service

router = APIRouter()


def _to_role_resp(r) -> RoleResponse:
    return RoleResponse(
        id=r.id,
        name=r.name,
        description=r.description,
        permissions=r.permissions,
        created_at=r.created_at,
    )


@router.post("/roles", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_role(
    payload: CreateRoleRequest,
    svc: RoleService = Depends(get_role_service),
) -> RoleResponse:
    try:
        return _to_role_resp(await svc.create_role(payload))
    except RoleAlreadyExists:
        raise HTTPException(status_code=409, detail="role_already_exists") from None


@router.get("/roles", response_model=list[RoleResponse])
async def list_roles(svc: RoleService = Depends(get_role_service)) -> list[RoleResponse]:
    return [_to_role_resp(r) for r in await svc.list_roles()]


@router.post("/assignments", response_model=AssignmentResponse, status_code=status.HTTP_201_CREATED)
async def assign(
    payload: AssignRoleRequest,
    svc: RoleService = Depends(get_role_service),
) -> AssignmentResponse:
    try:
        a = await svc.assign(payload.user_id, payload.role_id)
    except RoleNotFound:
        raise HTTPException(status_code=404, detail="role_not_found") from None
    except AssignmentAlreadyExists:
        raise HTTPException(status_code=409, detail="assignment_already_exists") from None
    role = (await svc.list_assignments(payload.user_id))[-1][1]
    return AssignmentResponse(
        user_id=a.user_id, role_id=a.role_id, role_name=role.name, assigned_at=a.assigned_at
    )


@router.delete("/assignments", status_code=status.HTTP_204_NO_CONTENT)
async def revoke(
    user_id: UUID,
    role_id: UUID,
    svc: RoleService = Depends(get_role_service),
) -> None:
    try:
        await svc.revoke(user_id, role_id)
    except RoleNotFound:
        raise HTTPException(status_code=404, detail="role_not_found") from None
    except AssignmentNotFound:
        raise HTTPException(status_code=404, detail="assignment_not_found") from None


@router.get("/users/{user_id}/roles", response_model=list[AssignmentResponse])
async def list_user_roles(
    user_id: UUID,
    svc: RoleService = Depends(get_role_service),
) -> list[AssignmentResponse]:
    result = []
    for a, role in await svc.list_assignments(user_id):
        result.append(
            AssignmentResponse(
                user_id=a.user_id,
                role_id=a.role_id,
                role_name=role.name,
                assigned_at=a.assigned_at,
            )
        )
    return result
