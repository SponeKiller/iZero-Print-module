from dataclasses import dataclass
from typing import ClassVar

from app.application.constants.templates.labels.footer import FooterLabel
from app.application.constants.templates.variants.footer import FooterVariant


@dataclass(frozen=True)
class FooterComponent:
    """
    Component printing the footer repeated on every page.

    Attributes:
        variant: Visual variant of the footer.
    """

    name: ClassVar[str] = "footer"
    labels: ClassVar[type[FooterLabel]] = FooterLabel

    variant: FooterVariant
