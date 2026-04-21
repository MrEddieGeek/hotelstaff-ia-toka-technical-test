from __future__ import annotations


class DomainError(Exception):
    """Error base del dominio auth."""


class EmailAlreadyRegistered(DomainError):
    pass


class InvalidCredentials(DomainError):
    pass


class UserInactive(DomainError):
    pass


class InvalidRefreshToken(DomainError):
    pass
