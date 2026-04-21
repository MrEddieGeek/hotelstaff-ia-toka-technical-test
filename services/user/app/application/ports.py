from __future__ import annotations

from typing import Protocol
from uuid import UUID

from hotelstaff_shared.events import DomainEvent

from ..domain.entities import StaffUser


class UserRepository(Protocol):
    async def get_by_id(self, user_id: UUID) -> StaffUser | None: ...

    async def get_by_email(self, email: str) -> StaffUser | None: ...

    async def list_all(self, limit: int, offset: int) -> tuple[list[StaffUser], int]: ...

    async def add(self, user: StaffUser) -> StaffUser: ...

    async def update(self, user: StaffUser) -> StaffUser: ...

    async def delete(self, user_id: UUID) -> None: ...


class EventPublisher(Protocol):
    async def publish(self, event: DomainEvent) -> None: ...
