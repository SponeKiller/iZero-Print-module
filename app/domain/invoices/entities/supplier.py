from typing import Self

from app.domain.shared.validation import validate_text
from app.domain.shared.value_objects.address import Address
from app.domain.shared.value_objects.company_id import CompanyId
from app.domain.shared.value_objects.vat_id import VatId


class Supplier:
    """
    Represents the party issuing the invoice.

    Attributes:
        name: Name of the supplier.
        company_id: Company ID, if supplied.
        vat_id: VAT ID, None for a non-payer of VAT.
        address: Address of the supplier.
    """

    def __init__(
        self,
        name: str,
        company_id: CompanyId | None,
        vat_id: VatId | None,
        address: Address,
    ):
        self.name = name
        self.company_id = company_id
        self.vat_id = vat_id
        self.address = address

    @classmethod
    def create(
        cls,
        name: str,
        company_id: CompanyId | None,
        vat_id: VatId | None,
        address: Address,
    ) -> Self:
        """
        Creates a new supplier.

        Args:
            name: Name of the supplier.
            company_id: Company ID, if supplied.
            vat_id: VAT ID, None for a non-payer of VAT.
            address: Address of the supplier.

        Returns:
            The newly created supplier.

        Raises:
            DomainValidationError: If name is blank or too long.
        """
        cls._validate(name)

        return cls(
            name=name,
            company_id=company_id,
            vat_id=vat_id,
            address=address,
        )

    @staticmethod
    def _validate(name: str) -> None:
        """
        Validates the name.

        Raises:
            DomainValidationError: If name is blank or too long.
        """
        validate_text(name=name, max_length=100)
