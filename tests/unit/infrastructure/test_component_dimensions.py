"""
Contract of dimensions between a parent and its children, checked for
every design without rendering anything.

Each variant of a component has `<name>/<variant>.dimensions.json`:

    needs: what the component needs from its parent
        min_width_mm: width it needs at least
        max_height_mm: the most it can be high (missing: it flows over
         pages)
    slots: places the component gives to its children, by their name
        width_mm, height_mm (height is optional)
    rows: the slots from top to bottom; slots of one row are side by side
    gap_mm: space between the slots of one row
    page: paper and its margins (document only)
"""
import json
from typing import Any

import pytest

from app.application.constants.templates.design.invoice import (
    InvoiceDesign,
)
from app.infrastructure.config import settings

DESIGNS = [design.value for design in InvoiceDesign]


def dimensions_of(component: Any) -> dict[str, Any]:
    file = (
        settings.templates_dir
        / component.name
        / f"{component.variant}.dimensions.json"
    )
    assert file.is_file(), f"{file} is missing"

    return json.loads(file.read_text(encoding="utf-8"))


def check(component: Any, width_mm: float, page_height_mm: float) -> None:
    """
    Checks one component placed into `width_mm` and then its children.
    """
    name = f"{component.name}/{component.variant}"
    dimensions = dimensions_of(component)
    needs = dimensions.get("needs", {})
    slots = dimensions.get("slots", {})
    rows = dimensions.get("rows", [])

    # every slot is placed in exactly one row
    assert sorted(slot for row in rows for slot in row) == sorted(slots), (
        f"{name}: rows do not match slots"
    )

    row_heights = []
    for row in rows:
        gaps = dimensions.get("gap_mm", 0) * (len(row) - 1)
        row_width = sum(slots[slot]["width_mm"] for slot in row) + gaps

        assert row_width <= width_mm, (
            f"{name}: row {row} is {row_width} mm wide,"
            f" only {width_mm} mm is available"
        )

        heights = []
        for slot in row:
            child = getattr(component, slot)
            child_name = f"{child.name}/{child.variant}"
            child_needs = dimensions_of(child).get("needs", {})

            assert child_needs["min_width_mm"] <= slots[slot]["width_mm"], (
                f"{name} gives {child_name} {slots[slot]['width_mm']} mm"
                f" of width, it needs {child_needs['min_width_mm']} mm"
            )

            height = child_needs.get("max_height_mm")
            if height is not None:
                offered = slots[slot].get("height_mm", page_height_mm)

                assert height <= offered, (
                    f"{name} gives {child_name} {offered} mm of height,"
                    f" it needs {height} mm"
                )
                heights.append(height)

            check(child, slots[slot]["width_mm"], page_height_mm)

        row_heights.append(max(heights, default=0))

    # what cannot flow over pages has to fit into what the component
    # itself can take
    if "max_height_mm" in needs:
        assert sum(row_heights) <= needs["max_height_mm"], (
            f"{name}: its children need {sum(row_heights)} mm of height,"
            f" it declares {needs['max_height_mm']} mm"
        )


@pytest.mark.parametrize("document", DESIGNS)
def test_page_gives_the_content_what_is_left_inside_the_margins(document):
    dimensions = dimensions_of(document)
    page = dimensions["page"]

    assert dimensions["slots"]["content"] == {
        "width_mm": (
            page["width_mm"]
            - page["margin_left_mm"]
            - page["margin_right_mm"]
        ),
        "height_mm": (
            page["height_mm"]
            - page["margin_top_mm"]
            - page["margin_bottom_mm"]
        ),
    }


@pytest.mark.parametrize("document", DESIGNS)
def test_every_parent_gives_its_children_enough_space(document):
    page = dimensions_of(document)["page"]
    content = dimensions_of(document)["slots"]["content"]

    check(
        document,
        width_mm=(
            page["width_mm"]
            - page["margin_left_mm"]
            - page["margin_right_mm"]
        ),
        page_height_mm=content["height_mm"],
    )


def test_child_that_needs_more_than_it_gets_is_reported(monkeypatch):
    # the supplier suddenly needs more width than the invoice gives it
    original = dimensions_of

    def wider_supplier(component):
        dimensions = original(component)
        if component.name == "supplier":
            dimensions["needs"]["min_width_mm"] = 120
        return dimensions

    monkeypatch.setattr(
        "tests.unit.infrastructure.test_component_dimensions.dimensions_of",
        wider_supplier,
    )

    with pytest.raises(AssertionError, match="it needs 120 mm"):
        test_every_parent_gives_its_children_enough_space(DESIGNS[0])
