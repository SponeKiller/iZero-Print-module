from dataclasses import dataclass
from typing import ClassVar

from app.application.constants.templates.labels.payments import PaymentsLabel
from app.application.constants.templates.variants.payments import (
    PaymentsVariant,
)


@dataclass(frozen=True)
class PaymentsComponent:
    """
    Component printing the payments.

    Attributes:
        variant: Visual variant of the payments.
    """

    name: ClassVar[str] = "payments"
    labels: ClassVar[type[PaymentsLabel]] = PaymentsLabel

    variant: PaymentsVariant
