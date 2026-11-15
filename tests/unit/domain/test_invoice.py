from datetime import date
from decimal import Decimal

import pytest

from app.domain.shared.exceptions.validation import (
    DomainValidationError,
    ProblemCode,
)
from app.domain.shared.value_objects.company_id import CompanyId
from app.domain.shared.value_objects.iban import Iban
from app.domain.shared.value_objects.vat_id import VatId
from tests.support import (
    VALID_IBAN,
    address,
    customer,
    invoice,
    item,
    payments,
    supplier,
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


def test_entity_fails_on_its_first_rejected_value():
    with pytest.raises(DomainValidationError) as raised:
        item(description="", quantity=Decimal(10000000000))

    assert raised.value.problem.field == "description"


def test_error_message_names_the_field():
    with pytest.raises(DomainValidationError) as raised:
        supplier(name="")

    assert str(raised.value) == "name: Is required."


def test_entity_takes_its_parts_already_built():
    # An entity never builds another object - the application layer does
    assert supplier(address=address(city="Brno")).address.city == "Brno"
