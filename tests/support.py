"""Test data and in-memory fakes of the ports shared by the tests."""
from datetime import date
from decimal import Decimal
from typing import Any

import pytest

from app.application.constants.document_formats import DocumentFormat
from app.application.dto.invoice.invoice import InvoiceOut
from app.application.dto.shared.component import Component
from app.application.dto.shared.document import DocumentOut
from app.application.use_cases.invoices.format_invoice import FormatInvoice
from app.domain.invoices.entities.customer import Customer
from app.domain.invoices.entities.invoice import Invoice
from app.domain.invoices.entities.invoice_item import InvoiceItem
from app.domain.invoices.entities.payments import Payments
from app.domain.invoices.entities.supplier import Supplier
from app.domain.shared.value_objects.address import Address
from app.domain.shared.value_objects.company_id import CompanyId
from app.domain.shared.value_objects.iban import Iban
from app.domain.shared.value_objects.vat_id import VatId

VALID_IBAN = "CZ6508000000192000145399"


# Builders of valid domain objects. Every keyword argument replaces the
# default value passed to `create` of the object.


def address(**overrides: Any) -> Address:
    return Address(
        **{
            "street": "Dlouhá 12",
            "city": "Praha",
            "postal_code": "110 00",
            "country": "Česká republika",
        }
        | overrides
    )


def supplier(**overrides: Any) -> Supplier:
    return Supplier.create(
        **{
            "name": "Dodavatel s.r.o.",
            "company_id": CompanyId("12345678"),
            "vat_id": VatId("CZ12345678"),
            "address": address(),
        }
        | overrides
    )


def customer(**overrides: Any) -> Customer:
    return Customer.create(
        **{
            "name": "Odběratel a.s.",
            "company_id": None,
            "vat_id": None,
            "address": address(
                street="Krátká 3", city="Brno", postal_code="602 00"
            ),
        }
        | overrides
    )


def item(**overrides: Any) -> InvoiceItem:
    return InvoiceItem.create(
        **{
            "description": "Konzultace",
            "quantity": Decimal("2.5"),
            "unit": "h",
            "unit_price": Decimal("1200.00"),
            "vat_rate": Decimal(21),
            "total": Decimal("3630.00"),
        }
        | overrides
    )


def item_without_unit_and_vat() -> InvoiceItem:
    return item(
        description="Licence",
        quantity=Decimal(1),
        unit=None,
        unit_price=Decimal("1234567.5"),
        vat_rate=None,
        total=Decimal("1234567.50"),
    )


def payments(**overrides: Any) -> Payments:
    return Payments.create(
        **{
            "iban": Iban(VALID_IBAN),
            "amount_to_pay": Decimal("1238197.50"),
            "currency": "CZK",
            "variable_symbol": "20260042",
            "due_date": date(2026, 11, 16),
        }
        | overrides
    )


def invoice(**overrides: Any) -> Invoice:
    return Invoice.create(
        **{
            "number": "2026-0042",
            "issue_date": date(2026, 11, 2),
            "supplier": supplier(),
            "customer": customer(),
            "items": [item(), item_without_unit_and_vat()],
            "payments": payments(),
        }
        | overrides
    )


def invoice_json() -> dict[str, Any]:
    """Valid invoice data as the JSON body of the print endpoint."""
    return {
        "number": "2026-0042",
        "issue_date": "2026-11-02",
        "supplier": {
            "name": "Dodavatel s.r.o.",
            "company_id": "12345678",
            "vat_id": "CZ12345678",
            "address": {
                "street": "Dlouhá 12",
                "city": "Praha",
                "postal_code": "110 00",
                "country": "Česká republika",
            },
        },
        "customer": {
            "name": "Odběratel a.s.",
            "address": {
                "street": "Krátká 3",
                "city": "Brno",
                "postal_code": "602 00",
                "country": "Česká republika",
            },
        },
        "items": [
            {
                "description": "Konzultace",
                "quantity": "2.5",
                "unit": "h",
                "unit_price": 1200,
                "vat_rate": 21,
                "total": "3630.00",
            },
        ],
        "payments": {
            "iban": "CZ65 0800 0000 1920 0014 5399",
            "amount_to_pay": "3630.00",
            "currency": "CZK",
            "variable_symbol": "20260042",
            "due_date": "2026-11-16",
        },
    }


def formatted_invoice(**overrides: Any) -> InvoiceOut:
    """Valid invoice formatted for printing."""
    return FormatInvoice().execute(invoice(**overrides))


def formatted_document(**overrides: Any) -> DocumentOut:
    """Document with a valid invoice - the input of the template engine."""
    content = formatted_invoice(**overrides)

    return DocumentOut(title=f"Faktura {content.number}", content=content)


def weasyprint_missing() -> bool:
    """True where WeasyPrint's native libraries (Pango) are not installed."""
    try:
        import weasyprint  # noqa: F401
    except (ImportError, OSError):
        return True
    return False


requires_weasyprint = pytest.mark.skipif(
    weasyprint_missing(),
    reason="WeasyPrint native libraries (Pango) are not installed",
)


class FakeTemplateEngine:
    """In-memory template engine remembering what it was asked to fill."""

    def __init__(self, error: Exception | None = None) -> None:
        self.error = error
        self.components: list[Component] = []
        self.documents: list[DocumentOut] = []
        # formatted invoices of the documents
        self.filled: list[InvoiceOut] = []

    def fill(self, component: Component, data: DocumentOut) -> str:
        if self.error is not None:
            raise self.error
        self.components.append(component)
        self.documents.append(data)
        self.filled.append(data.content)
        return f"<invoice {data.content.number}>"


class FakeDocumentRenderer:
    """In-memory renderer remembering what it rendered."""

    def __init__(self, error: Exception | None = None) -> None:
        self.error = error
        self.rendered: list[str] = []
        self.formats: list[DocumentFormat] = []

    def render(self, document: str, document_format: DocumentFormat) -> bytes:
        if self.error is not None:
            raise self.error
        self.rendered.append(document)
        self.formats.append(document_format)
        return b"%PDF-fake " + document.encode()
