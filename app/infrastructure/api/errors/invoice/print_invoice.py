from fastapi import status

from app.application.exceptions.base import ApplicationError
from app.application.exceptions.printing import (
    DocumentRenderingError,
    InvalidDocumentDataError,
    TemplateFillingError,
)
from app.infrastructure.api.schemas.message_id import MessageId

PRINT_ERRORS: dict[type[ApplicationError], tuple[MessageId, int]] = {
    InvalidDocumentDataError: (
        MessageId.PRINT_INVALID_DATA,
        status.HTTP_422_UNPROCESSABLE_ENTITY,
    ),
    TemplateFillingError: (
        MessageId.PRINT_TEMPLATE_FILLING_FAILED,
        status.HTTP_500_INTERNAL_SERVER_ERROR,
    ),
    DocumentRenderingError: (
        MessageId.PRINT_RENDERING_FAILED,
        status.HTTP_500_INTERNAL_SERVER_ERROR,
    ),
}
