
from app.application.constants.document_formats import DocumentFormat
from app.infrastructure.services.chromium_document_renderer import (
    ChromiumDocumentRenderer,
)


def test_renders_the_document_into_a_pdf():
    document = (
        "<html><head><style>@page { size: A4; margin: 10mm }</style></head>"
        "<body><h1>Faktura</h1></body></html>"
    )

    content = ChromiumDocumentRenderer().render(document, DocumentFormat.PDF)

    assert content.startswith(b"%PDF-")
    assert content.rstrip().endswith(b"%%EOF")

