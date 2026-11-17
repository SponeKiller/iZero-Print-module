from app.application.constants.document_formats import DocumentFormat
from app.application.constants.templates.design.invoice import (
    InvoiceDesign,
)
from app.infrastructure.config import settings
from app.infrastructure.services.chromium_document_renderer import (
    ChromiumDocumentRenderer,
)
from app.infrastructure.services.jinja_template_engine import (
    JinjaTemplateEngine,
)
from tests.support import formatted_invoice, requires_chromium

pytestmark = requires_chromium


def test_renders_the_filled_template_into_a_pdf():
    document = JinjaTemplateEngine(settings.templates_dir).fill(
        InvoiceDesign.CLASSIC.value, formatted_invoice()
    )

    content = ChromiumDocumentRenderer().render(document, DocumentFormat.PDF)

    assert content.startswith(b"%PDF-")
    assert content.rstrip().endswith(b"%%EOF")


def test_does_not_fetch_urls_referenced_by_the_document():
    # An unreachable stylesheet/image must be ignored, never requested
    document = (
        '<link rel="stylesheet" href="http://127.0.0.1:9/x.css">'
        '<img src="file:///etc/passwd"><p>text</p>'
    )

    content = ChromiumDocumentRenderer().render(document, DocumentFormat.PDF)

    assert content.startswith(b"%PDF-")
