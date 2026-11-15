from dataclasses import dataclass

from app.application.dto.shared.address import AddressIn, AddressOut


@dataclass(frozen=True, kw_only=True)
class CustomerIn:
    """DTO carrying a supplied customer."""
    name: str
    company_id: str | None = None
    vat_id: str | None = None
    address: AddressIn


@dataclass(frozen=True, kw_only=True)
class CustomerOut:
    """DTO carrying a customer formatted for printing."""
    name: str
    company_id: str | None
    vat_id: str | None
    address: AddressOut
