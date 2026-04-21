from __future__ import annotations

from fastapi import APIRouter, Depends

from ...infrastructure.security.jwt_service import RS256TokenService
from ..deps import get_token_service

router = APIRouter()


@router.get("/jwks.json")
async def jwks(tokens: RS256TokenService = Depends(get_token_service)) -> dict:
    return tokens.jwks()
