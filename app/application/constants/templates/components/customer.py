from dataclasses import dataclass
from typing import ClassVar

from app.application.constants.templates.components.address import (
    AddressComponent,
)
from app.application.constants.templates.labels.customer import CustomerLabel
from app.application.constants.templates.variants.customer import (
    CustomerVariant,
)


@dataclass(frozen=True)
class CustomerComponent:
    """
    Component printing a customer.

    Attributes:
        variant: Visual variant of the customer.
        address: Component printing the address of the customer.
    """

    name: ClassVar[str] = "customer"
    labels: ClassVar[type[CustomerLabel]] = CustomerLabel

    variant: CustomerVariant
    address: AddressComponent
