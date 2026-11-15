from dataclasses import dataclass

from app.domain.shared.validation import validate_text


@dataclass(frozen=True)
class Address:
    """
    Postal address of a supplier or a customer.

    Attributes:
        street: Street with the house number.
        city: City.
        postal_code: Postal code.
        country: Name of the country.

    Raises:
        DomainValidationError: If a value is missing or too long.
    """

    street: str
    city: str
    postal_code: str
    country: str

    def __post_init__(self):
        validate_text(street=self.street, max_length=100)
        validate_text(city=self.city, max_length=100)
        validate_text(postal_code=self.postal_code, max_length=10)
        validate_text(country=self.country, max_length=50)
