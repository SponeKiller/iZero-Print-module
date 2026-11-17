from decimal import Decimal

from pydantic import BaseModel


class InvoiceItemSchemaIn(BaseModel):
    """Schema carrying an invoice item."""

    description: str
    quantity: Decimal
    unit: str | None = None
    unit_price: Decimal
    vat_rate: Decimal | None = None
    total: Decimal
