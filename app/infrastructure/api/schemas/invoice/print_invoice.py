from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.domain.shared.exceptions.validation import ProblemCode

# The request schemas give the body its shape: which values are required
# and their data types. Lengths are checked by the domain.


class AddressSchemaIn(BaseModel):
    """Schema carrying an address."""

    street: str
    city: str
    postal_code: str
    country: str


class SupplierSchemaIn(BaseModel):
    """Schema carrying a supplier."""

    name: str
    company_id: str | None = None
    vat_id: str | None = None
    address: AddressSchemaIn


class CustomerSchemaIn(BaseModel):
    """Schema carrying a customer."""

    name: str
    company_id: str | None = None
    vat_id: str | None = None
    address: AddressSchemaIn


class InvoiceItemSchemaIn(BaseModel):
    """Schema carrying an invoice item."""

    description: str
    quantity: Decimal
    unit: str | None = None
    unit_price: Decimal
    vat_rate: Decimal | None = None
    total: Decimal


class PaymentsSchemaIn(BaseModel):
    """Schema carrying banking details and the amount to pay."""

    iban: str
    amount_to_pay: Decimal
    currency: str
    variable_symbol: str | None = None
    due_date: date


class PrintInvoiceSchemaIn(BaseModel):
    """Schema carrying invoice data to print."""

    number: str
    issue_date: date
    supplier: SupplierSchemaIn
    customer: CustomerSchemaIn
    items: list[InvoiceItemSchemaIn] = Field(min_length=1)
    payments: PaymentsSchemaIn


class ValidationProblemSchemaOut(BaseModel):
    """Schema carrying one validation problem of the supplied data."""

    model_config = ConfigDict(from_attributes=True)

    code: ProblemCode
    field: str
    message: str
