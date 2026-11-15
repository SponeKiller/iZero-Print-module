from dataclasses import dataclass
from typing import ClassVar

from app.application.constants.templates.components.address import (
    AddressComponent,
)
from app.application.constants.templates.labels.supplier import SupplierLabel
from app.application.constants.templates.variants.supplier import (
    SupplierVariant,
)


@dataclass(frozen=True)
class SupplierComponent:
    """
    Component printing a supplier.

    Attributes:
        variant: Visual variant of the supplier.
        address: Component printing the address of the supplier.
    """

    name: ClassVar[str] = "supplier"
    labels: ClassVar[type[SupplierLabel]] = SupplierLabel

    variant: SupplierVariant
    address: AddressComponent
