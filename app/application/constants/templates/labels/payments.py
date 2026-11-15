from enum import StrEnum


class PaymentsLabel(StrEnum):
    """Labels printed with the payments."""

    DUE_DATE = "Datum splatnosti"
    IBAN = "IBAN"
    VARIABLE_SYMBOL = "Variabilní symbol"
    AMOUNT_TO_PAY = "Celkem k úhradě"
