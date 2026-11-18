from app.application.constants.document_formats import DocumentFormat


class FakeDocumentRenderer:
    """
    In-memory renderer remembering what it rendered.

    Attributes:
        error: Exception raised by every `render`, None to render normally.
        rendered: Documents it rendered.
        formats: Formats it rendered them in.
    """

    def __init__(self, error: Exception | None = None) -> None:
        self.error = error
        self.rendered: list[str] = []
        self.formats: list[DocumentFormat] = []

    def render(self, document: str, document_format: DocumentFormat) -> bytes:
        if self.error is not None:
            raise self.error
        self.rendered.append(document)
        self.formats.append(document_format)
        return b"%PDF-fake " + document.encode()
