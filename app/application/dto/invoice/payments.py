from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True, kw_only=True)
class PaymentsIn:
    """DTO carrying supplied payments."""
    iban: str
    amount_to_pay: Decimal
    currency: str
    variable_symbol: str | None = None
    due_date: date


@dataclass(frozen=True, kw_only=True)
class PaymentsOut:
    """DTO carrying payments formatted for printing."""
    iban: str
    amount_to_pay: str
    currency: str
    variable_symbol: str | None
    due_date: str
