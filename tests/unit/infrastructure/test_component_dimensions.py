"""
Contract of dimensions between a parent and its children, checked for
every design without rendering anything.

Each variant of a component has `<name>/<variant>.dimensions.json`, its
shape is `Dimensions` in `app/infrastructure/types/template_dimensions.py`.
"""
import json
from typing import Any

import pytest

from app.application.constants.templates.design.invoice import (
    InvoiceDesign,
)
from app.infrastructure.config import settings
from app.infrastructure.types.template_dimensions import Dimensions

DESIGNS = [design.value for design in InvoiceDesign]


def dimensions_of(component: Any) -> Dimensions:
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

        # Row has to fit to what parent offers
        gaps = dimensions.get("gap_mm", 0) * (len(row) - 1)
        row_width = sum(slots[slot]["width_mm"] for slot in row) + gaps
        assert row_width <= width_mm, (
            f"{name}: row {row} is {row_width} mm wide,"
            f" only {width_mm} mm is available"
        )

        # slots side by side form one line, must have same height
        slot_heights = {slot: slots[slot].get("height_mm") for slot in row}
        assert len(set(slot_heights.values())) == 1, (
            f"{name}: slots in row {row} differ in height: {slot_heights}"
        )

        row_heights.append(slot_heights[row[0]])

        for slot in row:
            child = getattr(component, slot)
            child_name = f"{child.name}/{child.variant}"
            child_needs = dimensions_of(child).get("needs", {})

            # Slot has to fit to set width from parent
            assert child_needs["max_width_mm"] <= slots[slot]["width_mm"], (
                f"{name} gives {child_name} {slots[slot]['width_mm']} mm"
                f" of width, it needs {child_needs['max_width_mm']} mm"
            )

            # a child that flows over pages cannot be put into a slot with
            # a limited height, except if its main component (document)
            # limited child has to fit into the slot or page if parent
            # has no limitation
            height = child_needs.get("max_height_mm")
            offered = slots[slot].get("height_mm")
            if height is None:
                assert offered is None or "page" in dimensions, (
                    f"{name} gives {child_name} {offered} mm of height,"
                    f" but it flows over component"
                )
            else:
                offered = page_height_mm if offered is None else offered
                assert height <= offered, (
                    f"{name} gives {child_name} {offered} mm of height,"
                    f" it needs {height} mm"
                )

            check(child, slots[slot]["width_mm"], page_height_mm)

    # If component has max height, it has to limit its child
    # to fit into that max height
    if "max_height_mm" in needs:
        assert None not in row_heights, (
            f"{name}: declares {needs['max_height_mm']} mm of height,"
            f" but some of its rows are not limited: {row_heights}"
        )
        assert sum(row_heights) <= needs["max_height_mm"], (
            f"{name}: its rows take {sum(row_heights)} mm of height,"
            f" it declares {needs['max_height_mm']} mm"
        )

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

