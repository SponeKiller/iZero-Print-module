from decimal import Decimal

from app.domain.shared.exceptions.validation import (
    DomainValidationError,
    ProblemCode,
    ValidationProblem,
)

# The checked value is passed as a keyword argument and its name is the
# name of the field reported in the problem, so the name is never written
# twice:
#
#     validate_text(description=description, max_length=200)
#
# Only the length is checked (and that a required string is not blank),
# never whether the value is correct.


def validate_text(
    *,
    max_length: int,
    required: bool = True,
    **field: str | None,
) -> None:
    """
    Checks a string.

    Args:
        max_length: Maximum number of characters.
        required: Whether the value has to be a non-blank string; an
         optional value may be None or blank.
        field: The checked value under the name of its field.

    Raises:
        DomainValidationError: If the value is blank although required or
         is too long.
    """
    ((name, value),) = field.items()

    if value is None or not value.strip():
        if required:
            _fail(ProblemCode.REQUIRED, name, "Is required.")
        return

    if len(value) > max_length:
        _fail(
            ProblemCode.TOO_LONG,
            name,
            f"Must have at most {max_length} characters.",
        )


def validate_decimal(*, max_digits: int, **field: Decimal | None) -> None:
    """
    Checks a decimal number. Only the space it takes is checked: the
    number of its digits, before and after the decimal point together
    (trailing zeros after the point and the sign do not count).

    Args:
        max_digits: Maximum number of digits in total.
        field: The checked value under the name of its field; None (an
         optional value that was not supplied) is not checked.

    Raises:
        DomainValidationError: If the value has too many digits.
    """
    ((name, value),) = field.items()

    if value is None:
        return

    _, digits, exponent = Decimal(value).normalize().as_tuple()
    # 0.5 has one digit before the point (the zero)
    integer_digits = max(len(digits) + exponent, 1)
    decimal_digits = max(-exponent, 0)

    if integer_digits + decimal_digits > max_digits:
        _fail(
            ProblemCode.TOO_LONG,
            name,
            f"Must have at most {max_digits} digits.",
        )


def _fail(code: ProblemCode, field: str, message: str) -> None:
    raise DomainValidationError(
        ValidationProblem(code=code, field=field, message=message)
    )
