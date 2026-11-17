from playwright.sync_api import Route, sync_playwright

from app.application.constants.document_formats import DocumentFormat
from app.application.ports.document_renderer import DocumentRenderer


class ChromiumDocumentRenderer(DocumentRenderer):
    """Renders an HTML document with headless Chromium (Playwright)."""

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
                f"Chromium cannot render {document_format}"
            )

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            try:
                page = browser.new_page(java_script_enabled=False)
                page.route("**/*", _block)
                page.set_content(document)

                return page.pdf(
                    prefer_css_page_size=True,
                    print_background=True,
                )
            finally:
                browser.close()


def _block(route: Route) -> None:
    route.abort()
