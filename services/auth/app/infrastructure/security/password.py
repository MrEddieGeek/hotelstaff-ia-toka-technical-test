from __future__ import annotations

from argon2 import PasswordHasher as _Argon2
from argon2.exceptions import VerifyMismatchError


class Argon2PasswordHasher:
    """Hashing con Argon2id — recomendado por OWASP."""

    def __init__(self) -> None:
        self._impl = _Argon2()

    def hash(self, plain: str) -> str:
        return self._impl.hash(plain)

    def verify(self, plain: str, hashed: str) -> bool:
        try:
            return self._impl.verify(hashed, plain)
        except VerifyMismatchError:
            return False
