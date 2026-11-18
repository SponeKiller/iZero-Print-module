from typing import Any

from app.application.constants.templates.design.invoice import (
    InvoiceDesign,
)
from app.application.constants.templates.labels.customer import CustomerLabel
from app.application.constants.templates.labels.footer import FooterLabel
from app.application.constants.templates.labels.invoice import InvoiceLabel
from app.application.constants.templates.labels.invoice_item import (
    InvoiceItemLabel,
)
from app.application.constants.templates.labels.payments import PaymentsLabel
from app.application.constants.templates.labels.supplier import SupplierLabel
from app.application.dto.invoice.customer import CustomerOut
from app.application.dto.invoice.invoice import InvoiceOut
from app.application.dto.invoice.invoice_item import InvoiceItemOut
from app.application.dto.invoice.payments import PaymentsOut
from app.application.dto.invoice.supplier import SupplierOut
from app.application.dto.shared.address import AddressOut
from app.infrastructure.config import settings
from app.infrastructure.services.jinja_template_engine import (
    JinjaTemplateEngine,
)

NBSP = "\u00a0"


def address_out(**overrides: Any) -> AddressOut:
    return AddressOut(
        **{
            "street": "Dlouhá 12",
            "city": "Praha",
            "postal_code": "110 00",
            "country": "Česká republika",
        }
        | overrides
    )


def supplier_out(**overrides: Any) -> SupplierOut:
    return SupplierOut(
        **{
            "name": "Dodavatel s.r.o.",
            "company_id": "12345678",
            "vat_id": "CZ12345678",
            "address": address_out(),
        }
        | overrides
    )


def customer_out(**overrides: Any) -> CustomerOut:
    return CustomerOut(
        **{
            "name": "Odběratel a.s.",
            "company_id": None,
            "vat_id": None,
            "address": address_out(
                street="Krátká 3", city="Brno", postal_code="602 00"
            ),
        }
        | overrides
    )


def item_out(**overrides: Any) -> InvoiceItemOut:
    return InvoiceItemOut(
        **{
            "description": "Konzultace",
            "quantity": "2,5",
            "unit": "h",
            "unit_price": f"1{NBSP}200,00",
            "vat_rate": "21",
            "total": f"3{NBSP}630,00",
        }
        | overrides
    )


def item_out_without_unit_and_vat() -> InvoiceItemOut:
    return item_out(
        description="Licence",
        quantity="1",
        unit=None,
        unit_price=f"1{NBSP}234{NBSP}567,50",
        vat_rate=None,
        total=f"1{NBSP}234{NBSP}567,50",
    )


def payments_out(**overrides: Any) -> PaymentsOut:
    return PaymentsOut(
        **{
            "iban": "CZ65 0800 0000 1920 0014 5399",
            "amount_to_pay": f"1{NBSP}238{NBSP}197,50",
            "currency": "CZK",
            "variable_symbol": "20260042",
            "due_date": f"16.{NBSP}11.{NBSP}2026",
        }
        | overrides
    )


def invoice_out(**overrides: Any) -> InvoiceOut:
    return InvoiceOut(
        **{
            "number": "2026-0042",
            "issue_date": f"2.{NBSP}11.{NBSP}2026",
            "supplier": supplier_out(),
            "customer": customer_out(),
            "items": [item_out(), item_out_without_unit_and_vat()],
            "payments": payments_out(),
        }
        | overrides
    )


DOCUMENT = InvoiceDesign.CLASSIC.value


def fill(invoice: InvoiceOut) -> str:
    return JinjaTemplateEngine(settings.templates_dir).fill(DOCUMENT, invoice)


def test_fills_every_supplied_value_and_label():
    html = fill(invoice_out())

    for expected in [
        "2026-0042",
        "Dodavatel s.r.o.",
        "Dlouhá 12",
        "110 00 Praha",
        "IČO: 12345678",
        "DIČ: CZ12345678",
        "Odběratel a.s.",
        "602 00 Brno",
        f"2.{NBSP}11.{NBSP}2026",
        f"16.{NBSP}11.{NBSP}2026",
        "CZ65 0800 0000 1920 0014 5399",
        "20260042",
        "Konzultace",
        "2,5",
        f"1{NBSP}200,00",
        "21&nbsp;%",
        f"3{NBSP}630,00",
        "Licence",
        f"1{NBSP}234{NBSP}567,50",
        f"1{NBSP}238{NBSP}197,50&nbsp;CZK",
    ]:
        assert expected in html

    for labels in [
        FooterLabel,
        InvoiceLabel,
        SupplierLabel,
        CustomerLabel,
        InvoiceItemLabel,
        PaymentsLabel,
    ]:
        for label in labels:
            assert label in html