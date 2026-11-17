from dataclasses import dataclass
from typing import ClassVar

from app.application.constants.templates.labels.invoice_item import (
    InvoiceItemLabel,
)
from app.application.constants.templates.variants.invoice_item import (
    InvoiceItemVariant,
)


@dataclass(frozen=True)
class InvoiceItemComponent:
    """
    Component printing every invoice item - it gets the list of the
    items and prints them as a whole (e.g. a table with its header).

    Attributes:
        variant: Visual variant of the items.
    """

    name: ClassVar[str] = "invoice_item"
    labels: ClassVar[type[InvoiceItemLabel]] = InvoiceItemLabel

    variant: InvoiceItemVariant
