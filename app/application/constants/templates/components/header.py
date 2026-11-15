from dataclasses import dataclass
from typing import ClassVar

from app.application.constants.templates.variants.header import HeaderVariant


@dataclass(frozen=True)
class HeaderComponent:
    """
    Component printing the header repeated on every page.

    Attributes:
        variant: Visual variant of the header.
    """

    name: ClassVar[str] = "header"
    labels: ClassVar[None] = None

    variant: HeaderVariant
