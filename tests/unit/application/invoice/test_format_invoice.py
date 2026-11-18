from datetime import date
from decimal import Decimal
from typing import Any

from app.application.dto.invoice.customer import CustomerOut
from app.application.dto.invoice.invoice_item import InvoiceItemOut
from app.application.dto.invoice.payments import PaymentsOut
from app.application.dto.invoice.supplier import SupplierOut
from app.application.dto.shared.address import AddressOut
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

NBSP = " "


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


def payments(**overrides: Any) -> Payments:
    return Payments.create(
        **{
            "iban": Iban("CZ6508000000192000145399"),
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
            "items": [
                item(),
                item(
                    description="Licence",
                    quantity=Decimal(1),
                    unit=None,
                    unit_price=Decimal("1234567.5"),
                    vat_rate=None,
                    total=Decimal("1234567.50"),
                ),
            ],
            "payments": payments(),
        }
        | overrides
    )


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
