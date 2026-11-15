from dataclasses import dataclass

from app.domain.shared.validation import validate_text


@dataclass(frozen=True)
class CompanyId:
    """
    Company identification number.

    Raises:
        DomainValidationError: If the value is blank or too long.
    """

    value: str

    def __post_init__(self):
        validate_text(company_id=self.value, max_length=8)
