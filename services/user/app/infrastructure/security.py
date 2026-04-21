from __future__ import annotations

from pathlib import Path

import jwt
from fastapi import Header, HTTPException, Request


def jwt_guard(auth_required: bool):
    async def _dep(
        request: Request,
        authorization: str | None = Header(default=None),
    ) -> dict | None:
        if not auth_required:
            return None
        if not authorization or not authorization.lower().startswith("bearer "):
            raise HTTPException(status_code=401, detail="missing_token")
        token = authorization.split(" ", 1)[1]
        verifier = request.app.state.jwt_verifier
        if verifier is None:
            raise HTTPException(status_code=503, detail="jwt_verifier_not_configured")
        try:
            claims = verifier.verify(token, audience=request.app.state.jwt_audience)
        except Exception as exc:
            raise HTTPException(status_code=401, detail=f"invalid_token: {exc}") from exc
        return claims

    return _dep


def build_verifier(public_key_path: str | None, issuer: str):
    if not public_key_path or not Path(public_key_path).exists():
        return None
    from hotelstaff_shared.security import JWTVerifier

    return JWTVerifier(public_key_path=public_key_path, algorithm="RS256", issuer=issuer)


__all__ = ["build_verifier", "jwt", "jwt_guard"]
