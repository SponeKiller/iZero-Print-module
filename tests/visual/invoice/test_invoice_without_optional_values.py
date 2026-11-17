"""
Visual test: invoice without any optional value (company IDs, VAT
IDs, unit, VAT rate, variable symbol), one page.
The printed PDF must look like `images/<platform>/test_invoice_without_optional_values*.png`
(see `tests/visual/compare_pdf.py`).
"""
from datetime import date
from decimal import Decimal

from app.application.dto.invoice.customer import CustomerIn
from app.application.dto.invoice.invoice import InvoiceIn
from app.application.dto.invoice.invoice_item import InvoiceItemIn
from app.application.dto.invoice.payments import PaymentsIn
from app.application.dto.invoice.supplier import SupplierIn
from app.application.dto.shared.address import AddressIn
from app.application.use_cases.invoices.print_invoice import PrintInvoice
from app.infrastructure.config import settings
from app.infrastructure.services.chromium_document_renderer import (
    ChromiumDocumentRenderer,
)
from app.infrastructure.services.jinja_template_engine import (
    JinjaTemplateEngine,
)
from tests.visual.compare_pdf import assert_pdf_looks_like

INVOICE = InvoiceIn(
    number="2026-0042",
    issue_date=date(2026, 11, 2),
    supplier=SupplierIn(
        name="Dodavatel s.r.o.",
        address=AddressIn(
            street="Dlouhá 12",
            city="Praha",
            postal_code="110 00",
            country="Česká republika",
        ),
    ),
    customer=CustomerIn(
        name="Odběratel a.s.",
        address=AddressIn(
            street="Krátká 3",
            city="Brno",
            postal_code="602 00",
            country="Česká republika",
        ),
    ),
    items=[
        InvoiceItemIn(
            description="Konzultace",
            quantity=Decimal(3),
            unit_price=Decimal("1000.00"),
            total=Decimal("3000.00"),
        ),
    ],
    payments=PaymentsIn(
        iban="CZ6508000000192000145399",
        amount_to_pay=Decimal("3000.00"),
        currency="CZK",
        due_date=date(2026, 11, 16),
    ),
)


def test_invoice_without_optional_values():
    pdf = PrintInvoice(
        JinjaTemplateEngine(settings.templates_dir),
        ChromiumDocumentRenderer(),
    ).execute(INVOICE).content

    assert_pdf_looks_like(pdf, __file__)
