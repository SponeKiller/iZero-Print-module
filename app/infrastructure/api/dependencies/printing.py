from functools import lru_cache

from app.application.ports.document_renderer import DocumentRenderer
from app.application.ports.template_engine import TemplateEngine
from app.infrastructure.config import settings
from app.infrastructure.services.chromium_document_renderer import (
    ChromiumDocumentRenderer,
)
from app.infrastructure.services.jinja_template_engine import (
    JinjaTemplateEngine,
)


# Creating same instance is expensive
@lru_cache
def get_template_engine() -> TemplateEngine:
    return JinjaTemplateEngine(settings.templates_dir)


def get_document_renderer() -> DocumentRenderer:
    return ChromiumDocumentRenderer()
