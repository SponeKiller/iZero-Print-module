from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class PaymentsSchemaIn(BaseModel):
    """Schema carrying banking details and the amount to pay."""

    iban: str
    amount_to_pay: Decimal
    currency: str
    variable_symbol: str | None = None
    due_date: date
