from dataclasses import dataclass
from typing import Any, ClassVar

from app.application.constants.templates.components.footer import (
    FooterComponent,
)
from app.application.constants.templates.components.header import (
    HeaderComponent,
)
from app.application.constants.templates.variants.document import (
    DocumentVariant,
)
from app.application.constants.templates.variants.footer import (
    FooterVariant,
)
from app.application.constants.templates.variants.header import (
    HeaderVariant,
)


@dataclass(frozen=True)
class DocumentComponent:
    """
    Component printing a document - the parent of everything printed.
    The variant is the type of the document: its page style (paper,
    margins, fonts, background) and its header and footer, which are
    fixed by the variant and never chosen separately.

    Attributes:
        variant: Type of the document.
        content: Component printing the content (e.g. an invoice).
    """

    name: ClassVar[str] = "document"
    labels: ClassVar[None] = None

    # Header and footer of every type of the document
    HEADERS: ClassVar[dict[DocumentVariant, HeaderComponent]] = {
        DocumentVariant.STANDARD: HeaderComponent(variant=HeaderVariant.NONE),
    }
    FOOTERS: ClassVar[dict[DocumentVariant, FooterComponent]] = {
        DocumentVariant.STANDARD: FooterComponent(
            variant=FooterVariant.PAGE_NUMBERS
        ),
    }

    variant: DocumentVariant
    content: Any

    @property
    def header(self) -> HeaderComponent:
        """Component printing the header of every page."""
        return self.HEADERS[self.variant]

    @property
    def footer(self) -> FooterComponent:
        """Component printing the footer of every page."""
        return self.FOOTERS[self.variant]
