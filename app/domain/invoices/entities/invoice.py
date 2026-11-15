from datetime import date
from typing import Self

from app.domain.invoices.entities.customer import Customer
from app.domain.invoices.entities.invoice_item import InvoiceItem
from app.domain.invoices.entities.payments import Payments
from app.domain.invoices.entities.supplier import Supplier
from app.domain.shared.validation import validate_text


class Invoice:
    """
    Represents an invoice.

    Attributes:
        number: Invoice number.
        issue_date: Date the invoice was issued.
        supplier: The party issuing the invoice.
        customer: The party the invoice is issued to.
        items: Lines of the invoice.
        payments: Banking details and the amount to pay.
    """

    def __init__(
        self,
        number: str,
        issue_date: date,
        supplier: Supplier,
        customer: Customer,
        items: list[InvoiceItem],
        payments: Payments,
    ):
        self.number = number
        self.issue_date = issue_date
        self.supplier = supplier
        self.customer = customer
        self.items = items
        self.payments = payments

    @classmethod
    def create(
        cls,
        number: str,
        issue_date: date,
        supplier: Supplier,
        customer: Customer,
        items: list[InvoiceItem],
        payments: Payments,
    ) -> Self:
        """
        Creates a new invoice.

        Args:
            number: Invoice number.
            issue_date: Date the invoice was issued.
            supplier: The party issuing the invoice.
            customer: The party the invoice is issued to.
            items: Lines of the invoice.
            payments: Banking details and the amount to pay.

        Returns:
            The newly created invoice.

        Raises:
            DomainValidationError: If number is blank or too long.
        """
        cls._validate(number)

        return cls(
            number=number,
            issue_date=issue_date,
            supplier=supplier,
            customer=customer,
            items=items,
            payments=payments,
        )

    @staticmethod
    def _validate(number: str) -> None:
        """
        Validates the number.

        Raises:
            DomainValidationError: If number is blank or too long.
        """
        validate_text(number=number, max_length=20)
