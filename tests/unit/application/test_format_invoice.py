from datetime import date
from decimal import Decimal

import pytest

from app.application.dto.invoice.customer import CustomerOut
from app.application.dto.invoice.invoice_item import InvoiceItemOut
from app.application.dto.invoice.payments import PaymentsOut
from app.application.dto.invoice.supplier import SupplierOut
from app.application.dto.shared.address import AddressOut
from app.application.use_cases.invoices.format_invoice import FormatInvoice
from app.domain.shared.value_objects.iban import Iban
from tests.support import invoice, item, payments

NBSP = " "


def test_formats_every_value_of_the_invoice():
    formatted = FormatInvoice().execute(invoice())

    assert formatted.number == "2026-0042"
    assert formatted.issue_date == f"2.{NBSP}11.{NBSP}2026"
    assert formatted.supplier == SupplierOut(
        name="Dodavatel s.r.o.",
        company_id="12345678",
        vat_id="CZ12345678",
        address=AddressOut(
            street="Dlouhá 12",
            city="Praha",
            postal_code="110 00",
            country="Česká republika",
        ),
    )
    assert formatted.customer == CustomerOut(
        name="Odběratel a.s.",
        company_id=None,
        vat_id=None,
        address=AddressOut(
            street="Krátká 3",
            city="Brno",
            postal_code="602 00",
            country="Česká republika",
        ),
    )
    assert formatted.items == [
        InvoiceItemOut(
            description="Konzultace",
            quantity="2,5",
            unit="h",
            unit_price=f"1{NBSP}200,00",
            vat_rate="21",
            total=f"3{NBSP}630,00",
        ),
        InvoiceItemOut(
            description="Licence",
            quantity="1",
            unit=None,
            unit_price=f"1{NBSP}234{NBSP}567,50",
            vat_rate=None,
            total=f"1{NBSP}234{NBSP}567,50",
        ),
    ]
    assert formatted.payments == PaymentsOut(
        iban="CZ65 0800 0000 1920 0014 5399",
        amount_to_pay=f"1{NBSP}238{NBSP}197,50",
        currency="CZK",
        variable_symbol="20260042",
        due_date=f"16.{NBSP}11.{NBSP}2026",
    )


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (Decimal(0), "0,00"),
        (Decimal("1234567.5"), f"1{NBSP}234{NBSP}567,50"),
        (Decimal(-150), "-150,00"),
        (Decimal("0.125"), "0,12"),
    ],
)
def test_money_has_two_decimal_places(value, expected):
    formatted = FormatInvoice().execute(invoice(items=[item(total=value)]))

    assert formatted.items[0].total == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (Decimal("2.50"), "2,5"),
        (Decimal(100), "100"),
        (Decimal("12.125"), "12,125"),
        (Decimal(12345), f"12{NBSP}345"),
        (Decimal(0), "0"),
    ],
)
def test_other_numbers_have_no_trailing_zeros(value, expected):
    formatted = FormatInvoice().execute(
        invoice(items=[item(quantity=value, vat_rate=value)])
    )

    assert formatted.items[0].quantity == expected
    assert formatted.items[0].vat_rate == expected


def test_iban_is_printed_in_groups_of_four():
    formatted = FormatInvoice().execute(
        invoice(payments=payments(iban=Iban("CZ6508000000192000145399")))
    )

    assert formatted.payments.iban == "CZ65 0800 0000 1920 0014 5399"


def test_does_not_validate_the_values():
    # Whatever the invoice holds is formatted as it is
    formatted = FormatInvoice().execute(
        invoice(
            payments=payments(
                iban=Iban("XX1"),
                due_date=date(1, 1, 1),
            )
        )
    )

    assert formatted.payments.iban == "XX1"
    assert formatted.payments.due_date == f"1.{NBSP}1.{NBSP}1"
