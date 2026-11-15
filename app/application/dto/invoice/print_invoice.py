from dataclasses import dataclass

from app.application.constants.document_formats import DocumentFormat


@dataclass(frozen=True)
class PrintInvoiceOut:
    """Output DTO of PrintInvoice use-case: the printed invoice."""
    invoice_number: str
    content: bytes
    document_format: DocumentFormat
