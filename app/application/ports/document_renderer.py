from typing import Protocol

from app.application.constants.document_formats import DocumentFormat


class DocumentRenderer(Protocol):
    """
    Defines contract for turning a filled template into the printed
    document, independently of the rendering technology.
    """

    def render(self, document: str, document_format: DocumentFormat) -> bytes:
        """
        Renders the filled template in the requested format.

        Args:
            document: Filled template
            document_format: Format of the printed document

        Returns:
            Content of the printed document

        Raises:
            Exception: Any error means the document could not be rendered
        """
        ...
