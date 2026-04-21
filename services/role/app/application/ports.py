from __future__ import annotations

from typing import Protocol
from uuid import UUID

from hotelstaff_shared.events import DomainEvent

from ..domain.entities import Role, UserRoleAssignment


class RoleRepository(Protocol):
    async def add(self, role: Role) -> Role: ...

    async def get_by_id(self, role_id: UUID) -> Role | None: ...

    async def get_by_name(self, name: str) -> Role | None: ...

    async def list_all(self) -> list[Role]: ...


class AssignmentRepository(Protocol):
    async def add(self, assignment: UserRoleAssignment) -> UserRoleAssignment: ...

    async def remove(self, user_id: UUID, role_id: UUID) -> bool: ...

    async def list_for_user(self, user_id: UUID) -> list[UserRoleAssignment]: ...

    async def exists(self, user_id: UUID, role_id: UUID) -> bool: ...


class EventPublisher(Protocol):
    async def publish(self, event: DomainEvent) -> None: ...
