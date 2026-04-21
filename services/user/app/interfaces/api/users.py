from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from ...application.dto import (
    CreateUserRequest,
    UpdateUserRequest,
    UserListResponse,
    UserResponse,
)
from ...application.services import UserService
from ...domain.errors import EmailAlreadyExists, UserNotFound
from ..deps import get_user_service

router = APIRouter()


def _to_resp(u) -> UserResponse:
    return UserResponse(
        id=u.id,
        email=u.email,
        full_name=u.full_name,
        position=u.position,
        department=u.department,
        is_active=u.is_active,
        created_at=u.created_at,
        updated_at=u.updated_at,
    )


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: CreateUserRequest,
    svc: UserService = Depends(get_user_service),
) -> UserResponse:
    try:
        user = await svc.create(payload)
    except EmailAlreadyExists:
        raise HTTPException(status_code=409, detail="email_already_exists") from None
    return _to_resp(user)


@router.get("", response_model=UserListResponse)
async def list_users(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    svc: UserService = Depends(get_user_service),
) -> UserListResponse:
    items, total = await svc.list(limit=limit, offset=offset)
    return UserListResponse(items=[_to_resp(u) for u in items], total=total)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: UUID, svc: UserService = Depends(get_user_service)) -> UserResponse:
    try:
        return _to_resp(await svc.get(user_id))
    except UserNotFound:
        raise HTTPException(status_code=404, detail="user_not_found") from None


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    payload: UpdateUserRequest,
    svc: UserService = Depends(get_user_service),
) -> UserResponse:
    try:
        return _to_resp(await svc.update(user_id, payload))
    except UserNotFound:
        raise HTTPException(status_code=404, detail="user_not_found") from None


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: UUID, svc: UserService = Depends(get_user_service)) -> None:
    try:
        await svc.delete(user_id)
    except UserNotFound:
        raise HTTPException(status_code=404, detail="user_not_found") from None
