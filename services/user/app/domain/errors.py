from __future__ import annotations


class DomainError(Exception):
    pass


class UserNotFound(DomainError):
    pass


class EmailAlreadyExists(DomainError):
    pass
