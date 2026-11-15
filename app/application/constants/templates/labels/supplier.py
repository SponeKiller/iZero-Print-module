from enum import StrEnum


class SupplierLabel(StrEnum):
    """Labels printed with the supplier."""

    TITLE = "Dodavatel"
    COMPANY_ID = "IČO"
    VAT_ID = "DIČ"
