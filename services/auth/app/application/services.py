from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

from ..domain.entities import User
from ..domain.errors import (
    EmailAlreadyRegistered,
    InvalidCredentials,
    InvalidRefreshToken,
    UserInactive,
)
from .dto import TokenPair
from .ports import PasswordHasher, TokenService, UserRepository


class AuthService:
    def __init__(
        self,
        users: UserRepository,
        hasher: PasswordHasher,
        tokens: TokenService,
    ) -> None:
        self._users = users
        self._hasher = hasher
        self._tokens = tokens

    async def register(self, email: str, password: str) -> User:
        email = email.lower().strip()
        if await self._users.get_by_email(email):
            raise EmailAlreadyRegistered(email)
        user = User(
            id=uuid4(),
            email=email,
            password_hash=self._hasher.hash(password),
            is_active=True,
            created_at=datetime.now(UTC),
            roles=[],
        )
        return await self._users.add(user)

    async def login(self, email: str, password: str) -> TokenPair:
        user = await self._users.get_by_email(email.lower().strip())
        if not user or not self._hasher.verify(password, user.password_hash):
            raise InvalidCredentials()
        if not user.is_active:
            raise UserInactive()
        return self._issue_pair(user)

    async def refresh(self, refresh_token: str) -> TokenPair:
        try:
            claims = self._tokens.decode_refresh(refresh_token)
        except Exception as exc:
            raise InvalidRefreshToken(str(exc)) from exc
        user = await self._users.get_by_id(UUID(claims["sub"]))
        if not user or not user.is_active:
            raise InvalidRefreshToken("user not available")
        return self._issue_pair(user)

    def _issue_pair(self, user: User) -> TokenPair:
        access, expires_in = self._tokens.issue_access(subject=str(user.id), roles=user.roles)
        refresh, _ = self._tokens.issue_refresh(subject=str(user.id))
        return TokenPair(access_token=access, refresh_token=refresh, expires_in=expires_in)
