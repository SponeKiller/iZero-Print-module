from dataclasses import dataclass
from typing import ClassVar

from app.application.constants.templates.components.customer import (
    CustomerComponent,
)
from app.application.constants.templates.components.invoice_item import (
    InvoiceItemComponent,
)
from app.application.constants.templates.components.payments import (
    PaymentsComponent,
)
from app.application.constants.templates.components.supplier import (
    SupplierComponent,
)
from app.application.constants.templates.labels.invoice import InvoiceLabel
from app.application.constants.templates.variants.invoice import InvoiceVariant


@dataclass(frozen=True)
class InvoiceComponent:
    """
    Component printing an invoice. It has the same children as the
    invoice: the variant is the layout placing them on the paper, each
    child is the component filling its place.

    Attributes:
        variant: Layout of the invoice.
        supplier: Component printing the supplier.
        customer: Component printing the customer.
        items: Component printing every invoice item.
        payments: Component printing the payments.
    """

    name: ClassVar[str] = "invoice"
    labels: ClassVar[type[InvoiceLabel]] = InvoiceLabel

    variant: InvoiceVariant
    supplier: SupplierComponent
    customer: CustomerComponent
    items: InvoiceItemComponent
    payments: PaymentsComponent
