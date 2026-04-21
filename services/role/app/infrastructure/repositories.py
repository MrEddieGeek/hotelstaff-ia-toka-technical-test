from __future__ import annotations

from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..domain.entities import Role, UserRoleAssignment
from .db.models import RoleModel, UserRoleModel


class SqlAlchemyRoleRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, role: Role) -> Role:
        row = RoleModel(
            id=role.id,
            name=role.name,
            description=role.description,
            permissions=list(role.permissions),
        )
        self._session.add(row)
        await self._session.flush()
        await self._session.refresh(row)
        return _role_to_entity(row)

    async def get_by_id(self, role_id: UUID) -> Role | None:
        row = await self._session.get(RoleModel, role_id)
        return _role_to_entity(row) if row else None

    async def get_by_name(self, name: str) -> Role | None:
        res = await self._session.execute(select(RoleModel).where(RoleModel.name == name))
        row = res.scalar_one_or_none()
        return _role_to_entity(row) if row else None

    async def list_all(self) -> list[Role]:
        res = await self._session.execute(select(RoleModel).order_by(RoleModel.name))
        return [_role_to_entity(r) for r in res.scalars().all()]


class SqlAlchemyAssignmentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, assignment: UserRoleAssignment) -> UserRoleAssignment:
        row = UserRoleModel(user_id=assignment.user_id, role_id=assignment.role_id)
        self._session.add(row)
        await self._session.flush()
        await self._session.refresh(row)
        return UserRoleAssignment(
            user_id=row.user_id, role_id=row.role_id, assigned_at=row.assigned_at
        )

    async def remove(self, user_id: UUID, role_id: UUID) -> bool:
        res = await self._session.execute(
            delete(UserRoleModel)
            .where(UserRoleModel.user_id == user_id)
            .where(UserRoleModel.role_id == role_id)
        )
        return (res.rowcount or 0) > 0

    async def list_for_user(self, user_id: UUID) -> list[UserRoleAssignment]:
        res = await self._session.execute(
            select(UserRoleModel).where(UserRoleModel.user_id == user_id)
        )
        return [
            UserRoleAssignment(user_id=r.user_id, role_id=r.role_id, assigned_at=r.assigned_at)
            for r in res.scalars().all()
        ]

    async def exists(self, user_id: UUID, role_id: UUID) -> bool:
        res = await self._session.execute(
            select(UserRoleModel)
            .where(UserRoleModel.user_id == user_id)
            .where(UserRoleModel.role_id == role_id)
        )
        return res.scalar_one_or_none() is not None


def _role_to_entity(row: RoleModel) -> Role:
    return Role(
        id=row.id,
        name=row.name,
        description=row.description,
        permissions=list(row.permissions or []),
        created_at=row.created_at,
    )
