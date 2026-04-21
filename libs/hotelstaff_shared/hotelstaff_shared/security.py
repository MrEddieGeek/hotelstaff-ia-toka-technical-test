"""Validación distribuida de JWT (RS256).

Cada microservicio valida localmente con la clave pública cargada desde disco.
El auth-service es el único que firma; el resto sólo verifica.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import jwt
from jwt.exceptions import InvalidTokenError


class JWTVerifier:
    def __init__(self, public_key_path: str, algorithm: str, issuer: str) -> None:
        self._public_key = Path(public_key_path).read_text(encoding="utf-8")
        self._algorithm = algorithm
        self._issuer = issuer

    def verify(self, token: str, audience: str | None = None) -> dict[str, Any]:
        try:
            return jwt.decode(
                token,
                self._public_key,
                algorithms=[self._algorithm],
                issuer=self._issuer,
                audience=audience,
                options={"require": ["exp", "iat", "iss", "sub"]},
            )
        except InvalidTokenError as exc:
            raise InvalidJWTError(str(exc)) from exc


class InvalidJWTError(Exception):
    """Se lanza cuando el token es inválido, expirado o con claims faltantes."""
