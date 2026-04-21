from __future__ import annotations

from collections.abc import AsyncIterator

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from ..application.services import UserService
from ..infrastructure.repositories import SqlAlchemyUserRepository


async def get_session(request: Request) -> AsyncIterator[AsyncSession]:
    sm = request.app.state.sessionmaker
    async with sm() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


def get_publisher(request: Request):
    return request.app.state.publisher


def get_user_service(
    session: AsyncSession = Depends(get_session),
    publisher=Depends(get_publisher),
) -> UserService:
    return UserService(users=SqlAlchemyUserRepository(session), events=publisher)
