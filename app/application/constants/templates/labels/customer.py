from enum import StrEnum


class CustomerLabel(StrEnum):
    """Labels printed with the customer."""

    TITLE = "Odběratel"
    COMPANY_ID = "IČO"
    VAT_ID = "DIČ"
