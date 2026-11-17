from pydantic import BaseModel

from app.infrastructure.api.schemas.shared.address import AddressSchemaIn


class CustomerSchemaIn(BaseModel):
    """Schema carrying a customer."""

    name: str
    company_id: str | None = None
    vat_id: str | None = None
    address: AddressSchemaIn
