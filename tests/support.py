"""Test data and in-memory fakes of the ports shared by the tests."""
from datetime import date
from decimal import Decimal
from typing import Any

import pytest

from app.application.constants.document_formats import DocumentFormat
from app.application.dto.invoice.invoice import InvoiceOut
from app.application.dto.shared.component import Component
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
            "iban": "CZ6508000000192000145399",
            "amount_to_pay": "3630.00",
            "currency": "CZK",
            "variable_symbol": "20260042",
            "due_date": "2026-11-16",
        },
    }


def formatted_invoice(**overrides: Any) -> InvoiceOut:
    """Valid invoice formatted for printing."""
    return FormatInvoice().execute(invoice(**overrides))


def chromium_missing() -> bool:
    """True where the Chromium of Playwright is not installed."""
    from playwright.sync_api import Error, sync_playwright

    try:
        with sync_playwright() as playwright:
            playwright.chromium.launch().close()
    except Error:
        return True
    return False


requires_chromium = pytest.mark.skipif(
    chromium_missing(),
    reason="Chromium is not installed (playwright install chromium)",
)


class FakeTemplateEngine:
    """In-memory template engine remembering what it was asked to fill."""

    def __init__(self, error: Exception | None = None) -> None:
        self.error = error
        self.components: list[Component] = []
        self.filled: list[InvoiceOut] = []

    def fill(self, component: Component, data: InvoiceOut) -> str:
        if self.error is not None:
            raise self.error
        self.components.append(component)
        self.filled.append(data)
        return f"<invoice {data.number}>"


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
