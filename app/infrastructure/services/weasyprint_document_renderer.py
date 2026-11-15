from app.application.constants.document_formats import DocumentFormat
from app.application.ports.document_renderer import DocumentRenderer


class WeasyPrintDocumentRenderer(DocumentRenderer):
    """Renders an HTML document with WeasyPrint."""

    def render(self, document: str, document_format: DocumentFormat) -> bytes:
        """
        Renders the HTML document in the requested format.

        Args:
            document (str): HTML document
            document_format (DocumentFormat): format to render

        Returns:
            bytes: content of the rendered document

        Raises:
            NotImplementedError: If the format is not supported
        """
        if document_format != DocumentFormat.PDF:
            raise NotImplementedError(
                f"WeasyPrint cannot render {document_format}"
            )

        # Imported here, not at module level: importing WeasyPrint loads
        # the native Pango libraries and fails where they are missing
        # (e.g. plain Windows). The service must still start there - the
        # failure then surfaces as a rendering error of this call.
        from weasyprint import HTML
        from weasyprint.urls import URLFetcher

        # The template is self-contained, so the renderer is not allowed
        # to fetch any URL (no file or network access from a document).
        url_fetcher = URLFetcher(allowed_protocols=())

        return HTML(string=document, url_fetcher=url_fetcher).write_pdf()
