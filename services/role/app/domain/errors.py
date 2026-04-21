from __future__ import annotations


class DomainError(Exception):
    pass


class RoleNotFound(DomainError):
    pass


class RoleAlreadyExists(DomainError):
    pass


class AssignmentAlreadyExists(DomainError):
    pass


class AssignmentNotFound(DomainError):
    pass
