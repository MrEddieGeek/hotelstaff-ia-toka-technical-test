from __future__ import annotations

import base64
import uuid
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import jwt
from cryptography.hazmat.primitives import serialization


def _b64u(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


class RS256TokenService:
    """Emite/valida JWT RS256. Sólo auth-service posee la clave privada."""

    ALGORITHM = "RS256"
    KID = "hotelstaff-auth-v1"

    def __init__(
        self,
        *,
        private_key_pem: str,
        issuer: str,
        audience: str,
        access_ttl_seconds: int,
        refresh_ttl_seconds: int,
    ) -> None:
        self._private_key = private_key_pem
        self._issuer = issuer
        self._audience = audience
        self._access_ttl = access_ttl_seconds
        self._refresh_ttl = refresh_ttl_seconds
        self._public_key_obj = serialization.load_pem_private_key(
            private_key_pem.encode("utf-8"), password=None
        ).public_key()

    @classmethod
    def from_file(
        cls,
        private_key_path: str,
        *,
        issuer: str,
        audience: str,
        access_ttl_seconds: int,
        refresh_ttl_seconds: int,
    ) -> RS256TokenService:
        pem = Path(private_key_path).read_text(encoding="utf-8")
        return cls(
            private_key_pem=pem,
            issuer=issuer,
            audience=audience,
            access_ttl_seconds=access_ttl_seconds,
            refresh_ttl_seconds=refresh_ttl_seconds,
        )

    def issue_access(self, *, subject: str, roles: list[str]) -> tuple[str, int]:
        return self._issue(
            subject=subject, ttl=self._access_ttl, extra={"roles": roles, "typ": "access"}
        ), self._access_ttl

    def issue_refresh(self, *, subject: str) -> tuple[str, int]:
        return self._issue(
            subject=subject, ttl=self._refresh_ttl, extra={"typ": "refresh"}
        ), self._refresh_ttl

    def decode_refresh(self, token: str) -> dict[str, Any]:
        claims = jwt.decode(
            token,
            self._public_key_obj,
            algorithms=[self.ALGORITHM],
            audience=self._audience,
            issuer=self._issuer,
            options={"require": ["exp", "iat", "iss", "sub"]},
        )
        if claims.get("typ") != "refresh":
            raise jwt.InvalidTokenError("not a refresh token")
        return claims

    def _issue(self, *, subject: str, ttl: int, extra: dict[str, Any]) -> str:
        now = datetime.now(UTC)
        payload: dict[str, Any] = {
            "iss": self._issuer,
            "aud": self._audience,
            "sub": subject,
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(seconds=ttl)).timestamp()),
            "jti": str(uuid.uuid4()),
            **extra,
        }
        return jwt.encode(
            payload,
            self._private_key,
            algorithm=self.ALGORITHM,
            headers={"kid": self.KID},
        )

    def jwks(self) -> dict[str, Any]:
        numbers = self._public_key_obj.public_numbers()
        n = numbers.n.to_bytes((numbers.n.bit_length() + 7) // 8, "big")
        e = numbers.e.to_bytes((numbers.e.bit_length() + 7) // 8, "big")
        return {
            "keys": [
                {
                    "kty": "RSA",
                    "use": "sig",
                    "alg": self.ALGORITHM,
                    "kid": self.KID,
                    "n": _b64u(n),
                    "e": _b64u(e),
                }
            ]
        }
