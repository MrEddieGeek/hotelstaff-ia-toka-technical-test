from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

from hotelstaff_shared.events import (
    USER_CREATED,
    USER_DELETED,
    USER_UPDATED,
    DomainEvent,
)

from ..domain.entities import StaffUser
from ..domain.errors import EmailAlreadyExists, UserNotFound
from .dto import CreateUserRequest, UpdateUserRequest
from .ports import EventPublisher, UserRepository

SERVICE_NAME = "user-service"


class UserService:
    def __init__(self, users: UserRepository, events: EventPublisher) -> None:
        self._users = users
        self._events = events

    async def create(self, payload: CreateUserRequest) -> StaffUser:
        email = payload.email.lower().strip()
        if await self._users.get_by_email(email):
            raise EmailAlreadyExists(email)
        now = datetime.now(UTC)
        user = StaffUser(
            id=uuid4(),
            email=email,
            full_name=payload.full_name.strip(),
            position=payload.position.strip(),
            department=payload.department,
            is_active=True,
            created_at=now,
            updated_at=now,
        )
        saved = await self._users.add(user)
        await self._events.publish(
            DomainEvent(
                event_type=USER_CREATED,
                producer=SERVICE_NAME,
                payload={
                    "user_id": str(saved.id),
                    "email": saved.email,
                    "full_name": saved.full_name,
                    "position": saved.position,
                    "department": saved.department,
                },
            )
        )
        return saved

    async def get(self, user_id: UUID) -> StaffUser:
        user = await self._users.get_by_id(user_id)
        if not user:
            raise UserNotFound(str(user_id))
        return user

    async def list(self, limit: int, offset: int) -> tuple[list[StaffUser], int]:
        return await self._users.list_all(limit=limit, offset=offset)

    async def update(self, user_id: UUID, payload: UpdateUserRequest) -> StaffUser:
        user = await self._users.get_by_id(user_id)
        if not user:
            raise UserNotFound(str(user_id))
        if payload.full_name is not None:
            user.full_name = payload.full_name.strip()
        if payload.position is not None:
            user.position = payload.position.strip()
        if payload.department is not None:
            user.department = payload.department
        if payload.is_active is not None:
            user.is_active = payload.is_active
        user.updated_at = datetime.now(UTC)
        saved = await self._users.update(user)
        await self._events.publish(
            DomainEvent(
                event_type=USER_UPDATED,
                producer=SERVICE_NAME,
                payload={
                    "user_id": str(saved.id),
                    "email": saved.email,
                    "full_name": saved.full_name,
                    "position": saved.position,
                    "department": saved.department,
                    "is_active": saved.is_active,
                },
            )
        )
        return saved

    async def delete(self, user_id: UUID) -> None:
        user = await self._users.get_by_id(user_id)
        if not user:
            raise UserNotFound(str(user_id))
        await self._users.delete(user_id)
        await self._events.publish(
            DomainEvent(
                event_type=USER_DELETED,
                producer=SERVICE_NAME,
                payload={"user_id": str(user_id), "email": user.email},
            )
        )
