from app.application.dto.invoice.customer import CustomerOut
from app.application.dto.invoice.invoice import InvoiceOut
from app.application.dto.invoice.invoice_item import InvoiceItemOut
from app.application.dto.invoice.payments import PaymentsOut
from app.application.dto.invoice.supplier import SupplierOut
from app.application.dto.shared.address import AddressOut
from app.domain.invoices.entities.invoice import Invoice

# Thousands are separated by a non-breaking space, so a number never
# wraps in the middle
_NBSP = " "


class FormatInvoice:

    def execute(self, invoice: Invoice) -> InvoiceOut:
        """
        Format an invoice for printing: turn every value into the text
        that is printed. Nothing is validated - the invoice is expected
        to be valid.

        Formats: money `1 234 567,50`, other numbers `2,5` (no trailing
        zeros), date `2. 11. 2026`, IBAN in groups of four.

        Args:
            invoice: Validated invoice

        Returns:
            Formatted invoice
        """
        supplier = SupplierOut(
            name=invoice.supplier.name,
            company_id=(
                invoice.supplier.company_id.value
                if invoice.supplier.company_id is not None
                else None
            ),
            vat_id=(
                invoice.supplier.vat_id.value
                if invoice.supplier.vat_id is not None
                else None
            ),
            address=AddressOut(
                street=invoice.supplier.address.street,
                city=invoice.supplier.address.city,
                postal_code=invoice.supplier.address.postal_code,
                country=invoice.supplier.address.country,
            ),
        )

        customer = CustomerOut(
            name=invoice.customer.name,
            company_id=(
                invoice.customer.company_id.value
                if invoice.customer.company_id is not None
                else None
            ),
            vat_id=(
                invoice.customer.vat_id.value
                if invoice.customer.vat_id is not None
                else None
            ),
            address=AddressOut(
                street=invoice.customer.address.street,
                city=invoice.customer.address.city,
                postal_code=invoice.customer.address.postal_code,
                country=invoice.customer.address.country,
            ),
        )

        items = [
            InvoiceItemOut(
                description=item.description,
                quantity=f"{item.quantity.normalize():,f}"
                .replace(",", _NBSP)
                .replace(".", ","),
                unit=item.unit,
                unit_price=f"{item.unit_price:,.2f}"
                .replace(",", _NBSP)
                .replace(".", ","),
                vat_rate=(
                    f"{item.vat_rate.normalize():,f}"
                    .replace(",", _NBSP)
                    .replace(".", ",")
                    if item.vat_rate is not None
                    else None
                ),
                total=f"{item.total:,.2f}"
                .replace(",", _NBSP)
                .replace(".", ","),
            )
            for item in invoice.items
        ]

        # Grouped by four, whatever grouping it was supplied in
        iban = "".join(invoice.payments.iban.value.split())
        issue_date = invoice.issue_date
        due_date = invoice.payments.due_date

        payments = PaymentsOut(
            iban=" ".join(iban[i:i + 4] for i in range(0, len(iban), 4)),
            amount_to_pay=f"{invoice.payments.amount_to_pay:,.2f}"
            .replace(",", _NBSP)
            .replace(".", ","),
            currency=invoice.payments.currency,
            variable_symbol=invoice.payments.variable_symbol,
            due_date=(
                f"{due_date.day}.{_NBSP}{due_date.month}.{_NBSP}"
                f"{due_date.year}"
            ),
        )

        return InvoiceOut(
            number=invoice.number,
            issue_date=(
                f"{issue_date.day}.{_NBSP}{issue_date.month}.{_NBSP}"
                f"{issue_date.year}"
            ),
            supplier=supplier,
            customer=customer,
            items=items,
            payments=payments,
        )
