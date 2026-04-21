from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..domain.entities import StaffUser
from .db.models import StaffUserModel


class SqlAlchemyUserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, user_id: UUID) -> StaffUser | None:
        row = await self._session.get(StaffUserModel, user_id)
        return _to_entity(row) if row else None

    async def get_by_email(self, email: str) -> StaffUser | None:
        result = await self._session.execute(
            select(StaffUserModel).where(StaffUserModel.email == email)
        )
        row = result.scalar_one_or_none()
        return _to_entity(row) if row else None

    async def list_all(self, limit: int, offset: int) -> tuple[list[StaffUser], int]:
        total = await self._session.scalar(select(func.count()).select_from(StaffUserModel)) or 0
        result = await self._session.execute(
            select(StaffUserModel)
            .order_by(StaffUserModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return [_to_entity(r) for r in result.scalars().all()], int(total)

    async def add(self, user: StaffUser) -> StaffUser:
        row = StaffUserModel(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            position=user.position,
            department=user.department,
            is_active=user.is_active,
        )
        self._session.add(row)
        await self._session.flush()
        await self._session.refresh(row)
        return _to_entity(row)

    async def update(self, user: StaffUser) -> StaffUser:
        row = await self._session.get(StaffUserModel, user.id)
        assert row is not None
        row.full_name = user.full_name
        row.position = user.position
        row.department = user.department
        row.is_active = user.is_active
        await self._session.flush()
        await self._session.refresh(row)
        return _to_entity(row)

    async def delete(self, user_id: UUID) -> None:
        row = await self._session.get(StaffUserModel, user_id)
        if row:
            await self._session.delete(row)
            await self._session.flush()


def _to_entity(row: StaffUserModel) -> StaffUser:
    return StaffUser(
        id=row.id,
        email=row.email,
        full_name=row.full_name,
        position=row.position,
        department=row.department,
        is_active=row.is_active,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )
