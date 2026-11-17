from fastapi import status

from app.application.exceptions.base import ApplicationError
from app.application.exceptions.printing import InvalidDocumentDataError
from app.infrastructure.api.schemas.message_id import MessageId

PRINT_ERRORS: dict[type[ApplicationError], tuple[MessageId, int]] = {
    InvalidDocumentDataError: (
        MessageId.PRINT_INVALID_DATA,
        status.HTTP_422_UNPROCESSABLE_ENTITY,
    ),
}
