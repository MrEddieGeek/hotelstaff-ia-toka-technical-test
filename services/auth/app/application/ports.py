from __future__ import annotations

from typing import Protocol
from uuid import UUID

from ..domain.entities import User


class UserRepository(Protocol):
    async def get_by_email(self, email: str) -> User | None: ...

    async def get_by_id(self, user_id: UUID) -> User | None: ...

    async def add(self, user: User) -> User: ...


class PasswordHasher(Protocol):
    def hash(self, plain: str) -> str: ...

    def verify(self, plain: str, hashed: str) -> bool: ...


class TokenService(Protocol):
    def issue_access(self, *, subject: str, roles: list[str]) -> tuple[str, int]: ...

    def issue_refresh(self, *, subject: str) -> tuple[str, int]: ...

    def decode_refresh(self, token: str) -> dict: ...
