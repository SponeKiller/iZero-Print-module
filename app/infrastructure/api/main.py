import sentry_sdk
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from app.application.exceptions.base import ApplicationError
from app.application.exceptions.printing import InvalidDocumentDataError
from app.domain.shared.exceptions.validation import ProblemCode
from app.infrastructure.api.errors import APPLICATION_ERRORS
from app.infrastructure.api.middleware.http_audit import HttpAuditMiddleware
from app.infrastructure.api.router import router
from app.infrastructure.api.schemas.base import JSONResponse, ResponseContainer
from app.infrastructure.api.schemas.message_id import MessageId
from app.infrastructure.api.schemas.shared.validation_problem import (
    ValidationProblemSchemaOut,
)
from app.infrastructure.config import settings

sentry_sdk.init(
    dsn=settings.sentry_dsn,
    environment=settings.sentry_environment,
    traces_sample_rate=settings.sentry_traces_sample_rate,
    send_default_pii=settings.sentry_send_default_pii,
)

app = FastAPI(title=settings.app_name)

#Middleware

##CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=True,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)

app.add_middleware(HttpAuditMiddleware)


#Routing

##API
app.include_router(router)

#Global exceptions
async def application_error_handler(request: Request, exc: ApplicationError):
    message_id, status_code = APPLICATION_ERRORS[type(exc)]

    data = None
    if isinstance(exc, InvalidDocumentDataError):
        data = [ValidationProblemSchemaOut.model_validate(exc.problem)]

    return JSONResponse(
        content=ResponseContainer(message_id=message_id, data=data),
        status_code=status_code,
    )

for application_error in APPLICATION_ERRORS:
    app.add_exception_handler(application_error, application_error_handler)

@app.exception_handler(RequestValidationError)
async def request_validation_error_handler(
    request: Request,
    exc: RequestValidationError,
):
    problems = []
    for error in exc.errors():
        field = ""
        for part in error["loc"][1:]:
            if isinstance(part, int):
                field += f"[{part}]"
            else:
                field += f".{part}" if field else part

        # too_short: the list of items is empty
        if error["type"] in ("missing", "too_short"):
            code = ProblemCode.REQUIRED
        elif error["type"] == "json_invalid":
            code, field = ProblemCode.INVALID_FORMAT, ""
        else:
            code = ProblemCode.INVALID_TYPE

        problems.append(
            ValidationProblemSchemaOut(
                code=code,
                field=field,
                message=error["msg"],
            )
        )

    return JSONResponse(
        content=ResponseContainer(
            message_id=MessageId.PRINT_INVALID_DATA,
            data=problems,
        ),
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    )

@app.exception_handler(Exception)
async def global_fallback_handler(request: Request, exc: Exception):
    sentry_sdk.capture_exception(exc)

    return JSONResponse(
        content=ResponseContainer(message_id=MessageId.SYSTEM_INTERNAL_FAIL),
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
