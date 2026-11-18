from app.application.dto.shared.component import Component


class FakeTemplateEngine[T]:
    """
    In-memory template engine remembering what it was asked to fill.

    Attributes:
        error: Exception raised by every `fill`, None to fill normally.
        components: Components it was asked to fill.
        filled: Data it was asked to fill them with.
    """

    DOCUMENT = "<filled document>"

    def __init__(self, error: Exception | None = None) -> None:
        self.error = error
        self.components: list[Component] = []
        self.filled: list[T] = []

    def fill(self, component: Component, data: T) -> str:
        if self.error is not None:
            raise self.error
        self.components.append(component)
        self.filled.append(data)
        return self.DOCUMENT
