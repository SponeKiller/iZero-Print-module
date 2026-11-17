from pydantic import BaseModel

from app.infrastructure.api.schemas.shared.address import AddressSchemaIn


class SupplierSchemaIn(BaseModel):
    """Schema carrying a supplier."""

    name: str
    company_id: str | None = None
    vat_id: str | None = None
    address: AddressSchemaIn
