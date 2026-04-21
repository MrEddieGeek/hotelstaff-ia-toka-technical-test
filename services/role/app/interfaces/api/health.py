from __future__ import annotations

from fastapi import APIRouter, status

router = APIRouter()


@router.get("/live", status_code=status.HTTP_200_OK)
async def live() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ready", status_code=status.HTTP_200_OK)
async def ready() -> dict[str, str]:
    return {"status": "ready"}
