from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, kw_only=True)
class DocumentOut:
    """
    DTO carrying a document formatted for printing.

    Attributes:
        title: Title of the document (e.g. `Faktura 2026-0042`).
        content: Formatted content of the document (e.g. InvoiceOut).
    """
    title: str
    content: Any
