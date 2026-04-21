from __future__ import annotations

from hotelstaff_shared.logging import get_logger

from ..application.dto import CreateUserRequest
from ..application.services import UserService
from ..infrastructure.events import NullEventPublisher
from ..infrastructure.repositories import SqlAlchemyUserRepository

log = get_logger(__name__)

DEMO_STAFF: list[CreateUserRequest] = [
    CreateUserRequest(
        email="ana.garcia@hotelstaff.mx",
        full_name="Ana García",
        position="Recepcionista",
        department="Front office",
    ),
    CreateUserRequest(
        email="luis.perez@hotelstaff.mx",
        full_name="Luis Pérez",
        position="Chef ejecutivo",
        department="Alimentos y bebidas",
    ),
    CreateUserRequest(
        email="maria.lopez@hotelstaff.mx",
        full_name="María López",
        position="Supervisora de housekeeping",
        department="Housekeeping",
    ),
    CreateUserRequest(
        email="carlos.ramirez@hotelstaff.mx",
        full_name="Carlos Ramírez",
        position="Técnico de mantenimiento",
        department="Mantenimiento",
    ),
]


async def seed_demo_users(sessionmaker, publisher) -> None:
    async with sessionmaker() as session:
        repo = SqlAlchemyUserRepository(session)
        existing, total = await repo.list_all(limit=1, offset=0)
        if existing or total:
            log.info("demo.staff.skip", reason="non_empty")
            return
        service = UserService(users=repo, publisher=publisher or NullEventPublisher())
        created = 0
        for payload in DEMO_STAFF:
            try:
                await service.create(payload)
                created += 1
            except Exception as exc:
                log.warning("demo.staff.create_failed", email=payload.email, error=str(exc))
        await session.commit()
        log.info("demo.staff.seeded", count=created)
