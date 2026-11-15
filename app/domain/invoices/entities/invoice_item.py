from decimal import Decimal
from typing import Self

from app.domain.shared.validation import validate_decimal, validate_text


class InvoiceItem:
    """
    Represents one line of the invoice. The amounts are kept as supplied,
    nothing is recalculated.

    Attributes:
        description: What is invoiced.
        quantity: Invoiced quantity.
        unit: Unit of the quantity (e.g. pcs, h), if supplied.
        unit_price: Price of one unit.
        vat_rate: VAT rate in percent, if supplied.
        total: Total of the line.
    """

    def __init__(
        self,
        description: str,
        quantity: Decimal,
        unit: str | None,
        unit_price: Decimal,
        vat_rate: Decimal | None,
        total: Decimal,
    ):
        self.description = description
        self.quantity = quantity
        self.unit = unit
        self.unit_price = unit_price
        self.vat_rate = vat_rate
        self.total = total

    @classmethod
    def create(
        cls,
        description: str,
        quantity: Decimal,
        unit: str | None,
        unit_price: Decimal,
        vat_rate: Decimal | None,
        total: Decimal,
    ) -> Self:
        """
        Creates a new invoice item.

        Args:
            description: What is invoiced.
            quantity: Invoiced quantity.
            unit: Unit of the quantity (e.g. pcs, h), if supplied.
            unit_price: Price of one unit.
            vat_rate: VAT rate in percent, if supplied.
            total: Total of the line.

        Returns:
            The newly created invoice item.

        Raises:
            DomainValidationError: If description is blank or a value is
                too long.
        """
        cls._validate(
            description, quantity, unit, unit_price, vat_rate, total
        )

        return cls(
            description=description,
            quantity=quantity,
            unit=unit,
            unit_price=unit_price,
            vat_rate=vat_rate,
            total=total,
        )

    @staticmethod
    def _validate(
        description: str,
        quantity: Decimal,
        unit: str | None,
        unit_price: Decimal,
        vat_rate: Decimal | None,
        total: Decimal,
    ) -> None:
        """
        Validates the supplied values.

        Raises:
            DomainValidationError: If description is blank or a value is
                too long.
        """
        validate_text(description=description, max_length=200)
        validate_decimal(quantity=quantity, max_digits=10)
        validate_text(unit=unit, max_length=10, required=False)
        validate_decimal(unit_price=unit_price, max_digits=12)
        validate_decimal(vat_rate=vat_rate, max_digits=5)
        validate_decimal(total=total, max_digits=12)
