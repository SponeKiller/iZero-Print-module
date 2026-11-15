from enum import StrEnum


class InvoiceLabel(StrEnum):
    """Labels printed on the invoice itself."""

    TITLE = "Faktura"
    NUMBER = "Číslo faktury"
    ISSUE_DATE = "Datum vystavení"
