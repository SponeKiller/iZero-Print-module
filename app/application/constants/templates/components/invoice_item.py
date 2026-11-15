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
    Component printing one invoice item.

    Attributes:
        variant: Visual variant of the item.
    """

    name: ClassVar[str] = "invoice_item"
    labels: ClassVar[type[InvoiceItemLabel]] = InvoiceItemLabel

    variant: InvoiceItemVariant
