from enum import StrEnum


class InvoiceItemLabel(StrEnum):
    """Labels printed with the invoice items."""

    DESCRIPTION = "Popis"
    QUANTITY = "Množství"
    UNIT = "MJ"
    UNIT_PRICE = "Cena za MJ"
    VAT_RATE = "DPH"
    TOTAL = "Celkem"
