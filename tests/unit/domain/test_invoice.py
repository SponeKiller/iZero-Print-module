from datetime import date
from decimal import Decimal
from typing import Any

import pytest

from app.domain.invoices.entities.customer import Customer
from app.domain.invoices.entities.invoice import Invoice
from app.domain.invoices.entities.invoice_item import InvoiceItem
from app.domain.invoices.entities.payments import Payments
from app.domain.invoices.entities.supplier import Supplier
from app.domain.shared.exceptions.validation import (
    DomainValidationError,
    ProblemCode,
)
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


def test_creates_invoice_from_valid_parts():
    created = invoice()

    assert created.number == "2026-0042"
    assert created.issue_date == date(2026, 11, 2)
    assert created.supplier.name == "Dodavatel s.r.o."
    assert created.supplier.company_id == CompanyId("12345678")
    assert created.supplier.vat_id == VatId("CZ12345678")
    assert created.supplier.address.city == "Praha"
    assert created.customer.company_id is None
    assert created.customer.vat_id is None
    assert len(created.items) == 2
    assert created.items[0].quantity == Decimal("2.5")
    assert created.items[1].unit is None
    assert created.items[1].vat_rate is None
    assert created.payments.iban == Iban(VALID_IBAN)
    assert created.payments.amount_to_pay == Decimal("1238197.50")
    assert created.payments.due_date == date(2026, 11, 16)


@pytest.mark.parametrize(
    ("build", "field", "value", "expected"),
    [
        # Invoice
        (invoice, "number", "", ProblemCode.REQUIRED),
        (invoice, "number", "   ", ProblemCode.REQUIRED),
        (invoice, "number", "x" * 21, ProblemCode.TOO_LONG),
        # Supplier / Customer
        (supplier, "name", "", ProblemCode.REQUIRED),
        (supplier, "name", "x" * 101, ProblemCode.TOO_LONG),
        (customer, "name", "  ", ProblemCode.REQUIRED),
        (customer, "name", "x" * 101, ProblemCode.TOO_LONG),
        # Items
        (item, "description", "", ProblemCode.REQUIRED),
        (item, "description", "x" * 201, ProblemCode.TOO_LONG),
        (item, "quantity", Decimal(10000000000), ProblemCode.TOO_LONG),
        (item, "quantity", Decimal("12345678.901"), ProblemCode.TOO_LONG),
        (item, "unit", "x" * 11, ProblemCode.TOO_LONG),
        (item, "unit_price", Decimal(1000000000000), ProblemCode.TOO_LONG),
        (item, "vat_rate", Decimal(100000), ProblemCode.TOO_LONG),
        (item, "vat_rate", Decimal("21.5555"), ProblemCode.TOO_LONG),
        (item, "total", Decimal("-1234567890.123"), ProblemCode.TOO_LONG),
        # Payments
        (payments, "amount_to_pay", Decimal("0.123456789012"),
         ProblemCode.TOO_LONG),
        (payments, "currency", "", ProblemCode.REQUIRED),
        (payments, "currency", "CZKK", ProblemCode.TOO_LONG),
        (payments, "variable_symbol", "12345678901", ProblemCode.TOO_LONG),
    ],
)
def test_entity_rejects_invalid_value(build, field, value, expected):
    with pytest.raises(DomainValidationError) as raised:
        build(**{field: value})

    problem = raised.value.problem

    # the field is named after the validated value
    assert (problem.field, problem.code) == (field, expected)


@pytest.mark.parametrize(
    ("build", "field", "value"),
    [
        (invoice, "number", "x" * 20),
        (supplier, "name", "x" * 100),
        (supplier, "vat_id", None),
        (supplier, "company_id", None),
        (customer, "company_id", CompanyId("12345678")),
        (item, "description", "x" * 200),
        (item, "quantity", Decimal(3)),
        (item, "quantity", Decimal("2.500")),
        (item, "unit", None),
        (item, "unit", ""),
        (item, "unit_price", Decimal("-150.00")),
        (item, "vat_rate", None),
        (item, "vat_rate", Decimal(0)),
        # Decimals: only the number of digits, wherever the point is
        (item, "quantity", Decimal(9999999999)),
        (item, "quantity", Decimal("99999999.99")),
        (item, "quantity", Decimal("1.234")),
        (item, "quantity", Decimal("0.123456789")),
        (item, "unit_price", Decimal("9999999999.99")),
        (item, "vat_rate", Decimal("21.555")),
        (item, "vat_rate", Decimal(99999)),
        (item, "total", Decimal("-123456789.123")),
        (payments, "amount_to_pay", Decimal("0.001")),
        # Strings: only the length, not the content
        (payments, "currency", "Kč"),
        (payments, "variable_symbol", None),
        (payments, "variable_symbol", "1234567890"),
        (payments, "variable_symbol", "12A"),
    ],
)
def test_entity_accepts_boundary_values(build, field, value):
    build(**{field: value})
