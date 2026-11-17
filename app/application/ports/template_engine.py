from typing import Any, Protocol

from app.application.dto.shared.component import Component


class TemplateEngine(Protocol):
    """
    Defines contract for filling the template of a component - the
    layout with places for the data - independently of the template
    technology.
    """

    def fill(self, component: Component, data: Any) -> str:
        """
        Fills the template of the component with the data. The template
        places its own values and its children, each child being filled
        the same way with its part of the data. The values are placed as
        they are - the engine does no formatting.

        Args:
            component: Component to fill, with its children
            data: Formatted data of what the component prints

        Returns:
            The filled template, in the markup the document renderer
            understands

        Raises:
            Exception: Any error means the template could not be filled
        """
        ...
