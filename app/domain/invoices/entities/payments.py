from datetime import date
from decimal import Decimal
from typing import Self

from app.domain.shared.validation import validate_decimal, validate_text
from app.domain.shared.value_objects.iban import Iban


class Payments:
    """
    Represents the banking details and the amount to pay.

    Attributes:
        iban: Bank account the invoice is paid to.
        amount_to_pay: Amount to pay.
        currency: Currency code (e.g. CZK).
        variable_symbol: Payment identifier, if supplied.
        due_date: Date the invoice is due.
    """

    def __init__(
        self,
        iban: Iban,
        amount_to_pay: Decimal,
        currency: str,
        variable_symbol: str | None,
        due_date: date,
    ):
        self.iban = iban
        self.amount_to_pay = amount_to_pay
        self.currency = currency
        self.variable_symbol = variable_symbol
        self.due_date = due_date

    @classmethod
    def create(
        cls,
        iban: Iban,
        amount_to_pay: Decimal,
        currency: str,
        variable_symbol: str | None,
        due_date: date,
    ) -> Self:
        """
        Creates new payments.

        Args:
            iban: Bank account the invoice is paid to.
            amount_to_pay: Amount to pay.
            currency: Currency code (e.g. CZK).
            variable_symbol: Payment identifier, if supplied.
            due_date: Date the invoice is due.

        Returns:
            The newly created payments.

        Raises:
            DomainValidationError: If currency is blank or a value is too
                long.
        """
        cls._validate(amount_to_pay, currency, variable_symbol)

        return cls(
            iban=iban,
            amount_to_pay=amount_to_pay,
            currency=currency,
            variable_symbol=variable_symbol,
            due_date=due_date,
        )

    @staticmethod
    def _validate(
        amount_to_pay: Decimal,
        currency: str,
        variable_symbol: str | None,
    ) -> None:
        """
        Validates the amount, currency and variable symbol.

        Raises:
            DomainValidationError: If currency is blank or a value is too
                long.
        """
        validate_decimal(amount_to_pay=amount_to_pay, max_digits=12)
        validate_text(currency=currency, max_length=3)
        validate_text(
            variable_symbol=variable_symbol, max_length=10, required=False
        )
