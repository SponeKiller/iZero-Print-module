from dataclasses import dataclass

from app.application.constants.document_formats import DocumentFormat


@dataclass(frozen=True)
class PrintInvoiceOut:
    """
    Output DTO of PrintInvoice use-case: the printed invoice.

    Attributes:
        filename: Name of the printed file (e.g. `invoice-2026-0042.pdf`).
        content: Content of the printed document.
        document_format: Format of the printed document.
    """
    filename: str
    content: bytes
    document_format: DocumentFormat
