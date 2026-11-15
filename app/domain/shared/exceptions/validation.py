from dataclasses import dataclass
from enum import StrEnum

from app.domain.shared.exceptions.errors import DomainError


class ProblemCode(StrEnum):
    """Stable identifiers of the reasons a supplied value is rejected."""

    REQUIRED = "required"
    INVALID_TYPE = "invalid_type"
    INVALID_FORMAT = "invalid_format"
    TOO_LONG = "too_long"


@dataclass(frozen=True)
class ValidationProblem:
    """
    One rejected value.

    Attributes:
        code: Stable identifier of the reason.
        field: Name of the rejected field (e.g. `name`).
        message: Human readable description.
    """

    code: ProblemCode
    field: str
    message: str


class DomainValidationError(DomainError):
    """
    Raised when a value breaks a validation rule. Carries the problem
    found.
    """

    def __init__(self, problem: ValidationProblem) -> None:
        self.problem = problem
        super().__init__(f"{problem.field}: {problem.message}")
