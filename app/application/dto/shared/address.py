from dataclasses import dataclass


@dataclass(frozen=True, kw_only=True)
class AddressIn:
    """DTO carrying a supplied address."""
    street: str
    city: str
    postal_code: str
    country: str


@dataclass(frozen=True, kw_only=True)
class AddressOut:
    """DTO carrying an address formatted for printing."""
    street: str
    city: str
    postal_code: str
    country: str
