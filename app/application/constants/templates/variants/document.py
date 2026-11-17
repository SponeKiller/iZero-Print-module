from enum import StrEnum


class DocumentVariant(StrEnum):
    """
    Types of a document: page style (paper, margins, fonts, background)
    and the header and footer that belong to it.
    """

    STANDARD = "standard"
