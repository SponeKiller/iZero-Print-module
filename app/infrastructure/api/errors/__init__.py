from app.application.exceptions.base import ApplicationError
from app.infrastructure.api.errors.invoice.print_invoice import PRINT_ERRORS
from app.infrastructure.api.schemas.message_id import MessageId

APPLICATION_ERRORS: dict[type[ApplicationError], tuple[MessageId, int]] = {
    **PRINT_ERRORS,
}
