from dataclasses import dataclass

from app.domain.shared.validation import validate_text


@dataclass(frozen=True)
class VatId:
    """
    VAT identification number (e.g. CZ12345678).

    Raises:
        DomainValidationError: If the value is blank or too long.
    """

    value: str

    def __post_init__(self):
        validate_text(vat_id=self.value, max_length=12)
