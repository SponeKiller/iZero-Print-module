from datetime import date
from decimal import Decimal
from typing import Any

from app.application.constants.document_formats import DocumentFormat
from app.application.constants.templates.design.invoice import (
    InvoiceDesign,
)
from app.application.dto.invoice.customer import CustomerIn
from app.application.dto.invoice.invoice import InvoiceIn, InvoiceOut
from app.application.dto.invoice.invoice_item import InvoiceItemIn
from app.application.dto.invoice.payments import PaymentsIn
from app.application.dto.invoice.supplier import SupplierIn
from app.application.dto.shared.address import AddressIn
from app.application.use_cases.invoices.print_invoice import PrintInvoice
from tests.support.fake_document_renderer import FakeDocumentRenderer
from tests.support.fake_template_engine import FakeTemplateEngine


def address_in(**overrides: Any) -> AddressIn:
    return AddressIn(
        **{
            "street": "Dlouhá 12",
            "city": "Praha",
            "postal_code": "110 00",
            "country": "Česká republika",
        }
        | overrides
    )


def supplier_in(**overrides: Any) -> SupplierIn:
    return SupplierIn(
        **{
            "name": "Dodavatel s.r.o.",
            "company_id": "12345678",
            "vat_id": "CZ12345678",
            "address": address_in(),
        }
        | overrides
    )


def customer_in(**overrides: Any) -> CustomerIn:
    return CustomerIn(
        **{
            "name": "Odběratel a.s.",
            "company_id": None,
            "vat_id": None,
            "address": address_in(
                street="Krátká 3", city="Brno", postal_code="602 00"
            ),
        }
        | overrides
    )


def item_in(**overrides: Any) -> InvoiceItemIn:
    return InvoiceItemIn(
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


def payments_in(**overrides: Any) -> PaymentsIn:
    return PaymentsIn(
        **{
            "iban": "CZ6508000000192000145399",
            "amount_to_pay": Decimal("1238197.50"),
            "currency": "CZK",
            "variable_symbol": "20260042",
            "due_date": date(2026, 11, 16),
        }
        | overrides
    )


def invoice_in(**overrides: Any) -> InvoiceIn:
    return InvoiceIn(
        **{
            "number": "2026-0042",
            "issue_date": date(2026, 11, 2),
            "supplier": supplier_in(),
            "customer": customer_in(),
            "items": [
                item_in(),
                item_in(
                    description="Licence",
                    quantity=Decimal(1),
                    unit=None,
                    unit_price=Decimal("1234567.5"),
                    vat_rate=None,
                    total=Decimal("1234567.50"),
                ),
            ],
            "payments": payments_in(),
        }
        | overrides
    )


def test_prints_valid_invoice():
    template = FakeTemplateEngine[InvoiceOut]()
    renderer = FakeDocumentRenderer()

    result = PrintInvoice(template, renderer).execute(invoice_in())

    # AC-2: the document is rendered from the template filled with the
    filled = template.filled[0]
    assert filled.number == "2026-0042"
    assert filled.supplier.company_id == "12345678"
    assert filled.customer.company_id is None
    assert filled.items[0].quantity == "2,5"
    assert filled.payments.iban == "CZ65 0800 0000 1920 0014 5399"
    # the application layer decides the design
    assert template.components == [InvoiceDesign.CLASSIC.value]
    assert renderer.rendered == [FakeTemplateEngine.DOCUMENT]
    assert result.content == (
        b"%PDF-fake " + FakeTemplateEngine.DOCUMENT.encode()
    )
    # the application layer decides the format
    assert renderer.formats == [DocumentFormat.PDF]
    assert result.document_format == DocumentFormat.PDF
    assert result.filename == "invoice-2026-0042.pdf"