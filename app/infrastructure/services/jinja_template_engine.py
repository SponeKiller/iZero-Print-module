import json
from pathlib import Path
from typing import Any

from jinja2 import (
    Environment,
    FileSystemLoader,
    StrictUndefined,
    TemplateNotFound,
)
from markupsafe import Markup

from app.application.dto.shared.component import Component
from app.application.ports.template_engine import TemplateEngine
from app.infrastructure.types.template_dimensions import Dimensions


class JinjaTemplateEngine(TemplateEngine):
    """
    Template engine over static Jinja2 files. The template of a
    component is the file `<name>/<variant>.html.jinja`, optionally with its
    styles in `<name>/<variant>.css.jinja` and its dimensions on the paper in
    `<name>/<variant>.dimensions.json`.

    Inside a file:
        component: the filled component (its children are its attributes)
        data: data of the filled component
        labels: labels of the filled component
        dimensions: dimensions of the filled component
        render(child, child_data): the filled child
        style(child, child_data): styles of the child; the data is
         needed only by styles that print it (header, footer)
    """

    def __init__(self, templates_dir: Path) -> None:
        """
        Args:
            templates_dir: Directory holding the template files
             (`TEMPLATES_DIR` in .env)
        """

        self.environment = Environment(
            loader=FileSystemLoader(templates_dir),
            autoescape=True,
            undefined=StrictUndefined,
        )
        self.templates_dir = templates_dir
        # Dimensions already read, by the file they were read from
        self.dimensions: dict[Path, Dimensions] = {}

    def fill(self, component: Component, data: Any) -> str:
        """
        Fills the HTML file of the component with the data.

        Args:
            component (Component): component to fill
            data (Any): data placed by the template

        Returns:
            str: HTML document (or its part, for a child)
        """
        template = self.environment.get_template(
            f"{component.name}/{component.variant}.html.jinja"
        )

        return template.render(
            component=component,
            data=data,
            labels=component.labels,
            dimensions=self._dimensions(component),
            render=self._render,
            style=self._style,
        )

    def _render(self, component: Component, data: Any) -> Markup:
        """
        Fills a child component; called from the file of its parent.

        Returns:
            Markup: HTML of the child, not escaped again by the parent
        """
        return Markup(self.fill(component, data))

    def _style(self, component: Component, data: Any = None) -> Markup:
        """
        Loads the styles of a component; called from the file of its
        parent.

        Returns:
            Markup: CSS of the component, empty if it has no styles
        """
        try:
            template = self.environment.get_template(
                f"{component.name}/{component.variant}.css.jinja"
            )
        except TemplateNotFound:
            return Markup("")

        return Markup(
            template.render(
                component=component,
                data=data,
                labels=component.labels,
                dimensions=self._dimensions(component),
                style=self._style,
            )
        )

    def _dimensions(self, component: Component) -> Dimensions:
        """
        Reads the dimensions of a component.

        Returns:
            Dimensions: content of the dimensions file, empty if the
            component has none
        """
        file = (
            self.templates_dir
            / component.name
            / f"{component.variant}.dimensions.json"
        )

        if file not in self.dimensions:
            self.dimensions[file] = (
                json.loads(file.read_text(encoding="utf-8"))
                if file.is_file()
                else {}
            )

        return self.dimensions[file]
