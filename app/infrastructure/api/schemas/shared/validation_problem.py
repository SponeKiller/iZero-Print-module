from pydantic import BaseModel, ConfigDict

from app.domain.shared.exceptions.validation import ProblemCode


class ValidationProblemSchemaOut(BaseModel):
    """Schema carrying one validation problem of the supplied data."""

    model_config = ConfigDict(from_attributes=True)

    code: ProblemCode
    field: str
    message: str
