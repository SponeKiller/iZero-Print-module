from app.application.exceptions.base import ApplicationError
from app.infrastructure.api.errors.invoice.print_invoice import PRINT_ERRORS
from app.infrastructure.api.schemas.message_id import MessageId

# Response of each application error. Endpoints let these errors propagate,
# so that get_db rolls the request's transaction back before the response
# is built.
APPLICATION_ERRORS: dict[type[ApplicationError], tuple[MessageId, int]] = {
    **PRINT_ERRORS,
}
