from datetime import date

from pydantic import BaseModel, Field

from app.infrastructure.api.schemas.invoice.customer import CustomerSchemaIn
from app.infrastructure.api.schemas.invoice.invoice_item import (
    InvoiceItemSchemaIn,
)
from app.infrastructure.api.schemas.invoice.payments import PaymentsSchemaIn
from app.infrastructure.api.schemas.invoice.supplier import SupplierSchemaIn

# The request schemas give the body its shape: which values are required
# and their data types. Lengths are checked by the domain.


class InvoiceSchemaIn(BaseModel):
    """Schema carrying invoice data to print."""

    number: str
    issue_date: date
    supplier: SupplierSchemaIn
    customer: CustomerSchemaIn
    items: list[InvoiceItemSchemaIn] = Field(min_length=1)
    payments: PaymentsSchemaIn
