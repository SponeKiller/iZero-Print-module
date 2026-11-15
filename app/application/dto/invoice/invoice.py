from dataclasses import dataclass
from datetime import date

from app.application.dto.invoice.customer import CustomerIn, CustomerOut
from app.application.dto.invoice.invoice_item import (
    InvoiceItemIn,
    InvoiceItemOut,
)
from app.application.dto.invoice.payments import PaymentsIn, PaymentsOut
from app.application.dto.invoice.supplier import SupplierIn, SupplierOut


@dataclass(frozen=True, kw_only=True)
class InvoiceIn:
    """Input DTO for PrintInvoice use-case: the supplied invoice."""
    number: str
    issue_date: date
    supplier: SupplierIn
    customer: CustomerIn
    items: list[InvoiceItemIn]
    payments: PaymentsIn


@dataclass(frozen=True, kw_only=True)
class InvoiceOut:
    """
    Output DTO of FormatInvoice use-case: the invoice with every value
    as the text to print. Optional values that were not supplied are
    None.
    """
    number: str
    issue_date: str
    supplier: SupplierOut
    customer: CustomerOut
    items: list[InvoiceItemOut]
    payments: PaymentsOut
