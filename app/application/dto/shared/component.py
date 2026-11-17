from enum import StrEnum
from typing import Protocol


class Component(Protocol):
    """
    DTO carrying one component to the template engine: one node of the
    tree a document is printed from. Its children are its attributes.
    """

    # What is printed (e.g. `invoice`, `supplier`)
    name: str
    # Which of its visual variants is used
    variant: StrEnum
    # Labels the component prints, None if it prints none
    labels: type[StrEnum] | None
