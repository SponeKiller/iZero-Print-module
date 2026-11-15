from dataclasses import replace
from datetime import date
from decimal import Decimal

import pytest

from app.application.constants.document_formats import DocumentFormat
from app.application.constants.templates.design.invoice import (
    InvoiceDesign,
)
from app.application.dto.invoice.customer import CustomerIn
from app.application.dto.invoice.invoice import InvoiceIn
from app.application.dto.invoice.invoice_item import InvoiceItemIn
from app.application.dto.invoice.payments import PaymentsIn
from app.application.dto.invoice.supplier import SupplierIn
from app.application.dto.shared.address import AddressIn
from app.application.exceptions.printing import (
    DocumentRenderingError,
    InvalidDocumentDataError,
    TemplateFillingError,
)
from app.application.use_cases.invoices.print_invoice import PrintInvoice
from app.domain.shared.exceptions.validation import ProblemCode
from tests.support import (
    VALID_IBAN,
    FakeDocumentRenderer,
    FakeTemplateEngine,
)

ADDRESS = AddressIn(
    street="Dlouhá 12",
    city="Praha",
    postal_code="110 00",
    country="Česká republika",
)

ITEM = InvoiceItemIn(
    description="Konzultace",
    quantity=Decimal("2.5"),
    unit="h",
    unit_price=Decimal(1200),
    vat_rate=Decimal(21),
    total=Decimal(3630),
)

PAYMENTS = PaymentsIn(
    iban=VALID_IBAN,
    amount_to_pay=Decimal(3630),
    currency="CZK",
    variable_symbol="20260042",
    due_date=date(2026, 11, 16),
)


def print_invoice_in() -> InvoiceIn:
    return InvoiceIn(
        number="2026-0042",
        issue_date=date(2026, 11, 2),
        supplier=SupplierIn(
            name="Dodavatel s.r.o.",
            company_id="12345678",
            vat_id="CZ12345678",
            address=ADDRESS,
        ),
        customer=CustomerIn(name="Odběratel a.s.", address=ADDRESS),
        items=[ITEM],
        payments=PAYMENTS,
    )


def test_prints_valid_invoice():
    template = FakeTemplateEngine()
    renderer = FakeDocumentRenderer()

    result = PrintInvoice(template, renderer).execute(print_invoice_in())

    # AC-2: the document is rendered from the template filled with the
    # supplied data
    assert [invoice.number for invoice in template.filled] == ["2026-0042"]
    # the application layer decides the design
    assert template.components == [InvoiceDesign.CLASSIC.value]
    assert template.documents[0].title == "Faktura 2026-0042"
    assert renderer.rendered == ["<invoice 2026-0042>"]
    assert result.content == b"%PDF-fake <invoice 2026-0042>"
    # the application layer decides the format
    assert renderer.formats == [DocumentFormat.PDF]
    assert result.document_format == DocumentFormat.PDF
    assert result.invoice_number == "2026-0042"


def test_invalid_data_is_rejected_and_nothing_is_printed():
    template = FakeTemplateEngine()
    renderer = FakeDocumentRenderer()
    dto = replace(
        print_invoice_in(),
        payments=replace(PAYMENTS, iban="CZ65" + "0" * 31),
    )

    with pytest.raises(InvalidDocumentDataError) as raised:
        PrintInvoice(template, renderer).execute(dto)

    # AC-1 / BR-2: the problem is returned, no template is filled and
    # nothing is rendered
    problem = raised.value.problem
    assert (problem.field, problem.code) == ("iban", ProblemCode.TOO_LONG)
    assert template.filled == []
    assert renderer.rendered == []


def test_domain_objects_are_built_from_the_supplied_data():
    template = FakeTemplateEngine()
    dto = replace(
        print_invoice_in(),
        payments=replace(
            PAYMENTS,
            iban="CZ65 0800 0000 1920 0014 5399",
            variable_symbol=None,
        ),
    )

    PrintInvoice(template, FakeDocumentRenderer()).execute(dto)

    # the template gets the invoice already formatted
    invoice = template.filled[0]
    assert invoice.supplier.company_id == "12345678"
    assert invoice.supplier.vat_id == "CZ12345678"
    assert invoice.supplier.address.city == "Praha"
    # optional values that were not supplied
    assert invoice.customer.company_id is None
    assert invoice.customer.vat_id is None
    assert invoice.payments.variable_symbol is None
    assert invoice.items[0].quantity == "2,5"
    assert invoice.payments.iban == "CZ65 0800 0000 1920 0014 5399"


@pytest.mark.parametrize(
    ("changes", "expected"),
    [
        (
            {"number": "x" * 21},
            ("number", ProblemCode.TOO_LONG),
        ),
        (
            {
                "supplier": SupplierIn(
                    name="Dodavatel s.r.o.",
                    vat_id="CZ12345678901",
                    address=ADDRESS,
                )
            },
            ("vat_id", ProblemCode.TOO_LONG),
        ),
        (
            {
                "customer": CustomerIn(
                    name="O", address=replace(ADDRESS, city="")
                )
            },
            ("city", ProblemCode.REQUIRED),
        ),
        (
            {
                "customer": CustomerIn(
                    name="O", company_id="123456789", address=ADDRESS
                )
            },
            ("company_id", ProblemCode.TOO_LONG),
        ),
        (
            {"items": [replace(ITEM, quantity=Decimal("12345678.901"))]},
            ("quantity", ProblemCode.TOO_LONG),
        ),
        (
            {"payments": replace(PAYMENTS, currency="CZKK")},
            ("currency", ProblemCode.TOO_LONG),
        ),
    ],
)
def test_invalid_value_is_rejected_by_the_domain(changes, expected):
    dto = replace(print_invoice_in(), **changes)

    with pytest.raises(InvalidDocumentDataError) as raised:
        PrintInvoice(FakeTemplateEngine(), FakeDocumentRenderer()).execute(
            dto
        )

    problem = raised.value.problem
    assert (problem.field, problem.code) == expected


def test_template_failure_is_a_print_error_and_nothing_is_rendered():
    cause = RuntimeError("template is broken")
    renderer = FakeDocumentRenderer()

    with pytest.raises(TemplateFillingError) as raised:
        PrintInvoice(FakeTemplateEngine(error=cause), renderer).execute(
            print_invoice_in()
        )

    assert raised.value.__cause__ is cause
    assert renderer.rendered == []


def test_rendering_failure_is_a_print_error():
    cause = OSError("cannot load library 'libpango'")

    with pytest.raises(DocumentRenderingError) as raised:
        PrintInvoice(
            FakeTemplateEngine(),
            FakeDocumentRenderer(error=cause),
        ).execute(print_invoice_in())

    assert raised.value.__cause__ is cause
