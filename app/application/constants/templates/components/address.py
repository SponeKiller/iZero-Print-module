from dataclasses import dataclass
from typing import ClassVar

from app.application.constants.templates.variants.address import AddressVariant


@dataclass(frozen=True)
class AddressComponent:
    """
    Component printing an address.

    Attributes:
        variant: Visual variant of the address.
    """

    name: ClassVar[str] = "address"
    labels: ClassVar[None] = None

    variant: AddressVariant
