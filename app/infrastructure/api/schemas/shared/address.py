from pydantic import BaseModel


class AddressSchemaIn(BaseModel):
    """Schema carrying an address."""

    street: str
    city: str
    postal_code: str
    country: str
