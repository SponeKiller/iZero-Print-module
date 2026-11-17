from typing import TypedDict

# Shape of `<name>/<variant>.dimensions.json` - the dimensions of one
# variant of a component on the paper. All lengths are in millimetres.
#
#     {
#       "needs": { "min_width_mm": 80, "max_height_mm": 110 },
#       "slots": { "address": { "width_mm": 80, "height_mm": 60 } },
#       "rows":  [["address"]],
#       "gap_mm": 10
#     }


class Needs(TypedDict, total=False):
    """
    What the component needs from its parent.

    Attributes:
        min_width_mm: Width it needs at least.
        max_height_mm: The most it can be high; missing when it flows
         over pages.
    """

    min_width_mm: int
    max_height_mm: int


class Slot(TypedDict, total=False):
    """
    Place the component gives to one of its children.

    Attributes:
        width_mm: Width of the place.
        height_mm: Height of the place; missing when it is not limited.
    """

    width_mm: int
    height_mm: int


class Page(TypedDict):
    """
    Paper of the document and its margins.

    Attributes:
        width_mm: Width of the paper.
        height_mm: Height of the paper.
        margin_top_mm: Top margin.
        margin_right_mm: Right margin.
        margin_bottom_mm: Bottom margin.
        margin_left_mm: Left margin.
    """

    width_mm: int
    height_mm: int
    margin_top_mm: int
    margin_right_mm: int
    margin_bottom_mm: int
    margin_left_mm: int


class Dimensions(TypedDict, total=False):
    """
    Dimensions of one variant of a component. Every key is optional: a
    component without children has no `slots`, only a document has a
    `page`.

    Attributes:
        needs: What the component needs from its parent.
        slots: Places given to its children, by the name of the child.
        rows: The slots from top to bottom; slots of one row are side by
         side.
        gap_mm: Space between the slots of one row.
        page: Paper and its margins (document only).
    """

    needs: Needs
    slots: dict[str, Slot]
    rows: list[list[str]]
    gap_mm: int
    page: Page
