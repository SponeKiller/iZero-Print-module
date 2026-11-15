from app.application.exceptions.base import ApplicationError
from app.domain.shared.exceptions.validation import ValidationProblem


class InvalidDocumentDataError(ApplicationError):
    """
    Specific error indicating that the supplied document data is invalid
    and nothing was printed. Carries the validation problem found.
    """

    def __init__(self, problem: ValidationProblem) -> None:
        super().__init__()
        self.problem = problem


class TemplateFillingError(ApplicationError):
    """Specific error indicating that filling the template failed."""


class DocumentRenderingError(ApplicationError):
    """Specific error indicating that rendering the document failed."""
