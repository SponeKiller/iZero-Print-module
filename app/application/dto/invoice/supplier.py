from dataclasses import dataclass

from app.application.dto.shared.address import AddressIn, AddressOut


@dataclass(frozen=True, kw_only=True)
class SupplierIn:
    """DTO carrying a supplied supplier."""
    name: str
    company_id: str | None = None
    vat_id: str | None = None
    address: AddressIn


@dataclass(frozen=True, kw_only=True)
class SupplierOut:
    """DTO carrying a supplier formatted for printing."""
    name: str
    company_id: str | None
    vat_id: str | None
    address: AddressOut
