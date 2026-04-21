from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

from hotelstaff_shared.events import ROLE_ASSIGNED, ROLE_REVOKED, DomainEvent

from ..domain.entities import Role, UserRoleAssignment
from ..domain.errors import (
    AssignmentAlreadyExists,
    AssignmentNotFound,
    RoleAlreadyExists,
    RoleNotFound,
)
from .dto import CreateRoleRequest
from .ports import AssignmentRepository, EventPublisher, RoleRepository

SERVICE_NAME = "role-service"


class RoleService:
    def __init__(
        self,
        roles: RoleRepository,
        assignments: AssignmentRepository,
        events: EventPublisher,
    ) -> None:
        self._roles = roles
        self._assignments = assignments
        self._events = events

    async def create_role(self, payload: CreateRoleRequest) -> Role:
        if await self._roles.get_by_name(payload.name):
            raise RoleAlreadyExists(payload.name)
        role = Role(
            id=uuid4(),
            name=payload.name,
            description=payload.description,
            permissions=list(payload.permissions),
            created_at=datetime.now(UTC),
        )
        return await self._roles.add(role)

    async def list_roles(self) -> list[Role]:
        return await self._roles.list_all()

    async def assign(self, user_id: UUID, role_id: UUID) -> UserRoleAssignment:
        role = await self._roles.get_by_id(role_id)
        if not role:
            raise RoleNotFound(str(role_id))
        if await self._assignments.exists(user_id, role_id):
            raise AssignmentAlreadyExists(f"{user_id}->{role_id}")
        assignment = UserRoleAssignment(
            user_id=user_id, role_id=role_id, assigned_at=datetime.now(UTC)
        )
        saved = await self._assignments.add(assignment)
        await self._events.publish(
            DomainEvent(
                event_type=ROLE_ASSIGNED,
                producer=SERVICE_NAME,
                payload={
                    "user_id": str(user_id),
                    "role_id": str(role_id),
                    "role_name": role.name,
                    "permissions": role.permissions,
                },
            )
        )
        return saved

    async def revoke(self, user_id: UUID, role_id: UUID) -> None:
        role = await self._roles.get_by_id(role_id)
        if not role:
            raise RoleNotFound(str(role_id))
        removed = await self._assignments.remove(user_id, role_id)
        if not removed:
            raise AssignmentNotFound(f"{user_id}->{role_id}")
        await self._events.publish(
            DomainEvent(
                event_type=ROLE_REVOKED,
                producer=SERVICE_NAME,
                payload={
                    "user_id": str(user_id),
                    "role_id": str(role_id),
                    "role_name": role.name,
                },
            )
        )

    async def list_assignments(self, user_id: UUID) -> list[tuple[UserRoleAssignment, Role]]:
        items = await self._assignments.list_for_user(user_id)
        result: list[tuple[UserRoleAssignment, Role]] = []
        for a in items:
            role = await self._roles.get_by_id(a.role_id)
            if role:
                result.append((a, role))
        return result
