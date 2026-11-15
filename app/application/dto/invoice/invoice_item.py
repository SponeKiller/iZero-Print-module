from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True, kw_only=True)
class InvoiceItemIn:
    """DTO carrying a supplied invoice item."""
    description: str
    quantity: Decimal
    unit: str | None = None
    unit_price: Decimal
    vat_rate: Decimal | None = None
    total: Decimal


@dataclass(frozen=True, kw_only=True)
class InvoiceItemOut:
    """DTO carrying an invoice item formatted for printing."""
    description: str
    quantity: str
    unit: str | None
    unit_price: str
    vat_rate: str | None
    total: str
