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


@dataclass(frozen=True)
class DocumentComponent:
    """
    Component printing a document - the parent of everything printed.
    The variant is the page style (paper, margins, fonts, background),
    the children are what is repeated on every page and the content.

    Attributes:
        variant: Page style of the document.
        header: Component printing the header of every page.
        footer: Component printing the footer of every page.
        content: Component printing the content (e.g. an invoice).
    """

    name: ClassVar[str] = "document"
    labels: ClassVar[None] = None

    variant: DocumentVariant
    header: HeaderComponent
    footer: FooterComponent
    content: Any
