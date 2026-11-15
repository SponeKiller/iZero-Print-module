from functools import lru_cache

from app.application.ports.document_renderer import DocumentRenderer
from app.application.ports.template_engine import TemplateEngine
from app.infrastructure.config import settings
from app.infrastructure.services.jinja_template_engine import (
    JinjaTemplateEngine,
)
from app.infrastructure.services.weasyprint_document_renderer import (
    WeasyPrintDocumentRenderer,
)

# Both adapters are stateless, so one instance serves every request (the
# Jinja environment caches the compiled templates).


@lru_cache
def get_template_engine() -> TemplateEngine:
    return JinjaTemplateEngine(settings.templates_dir)


@lru_cache
def get_document_renderer() -> DocumentRenderer:
    return WeasyPrintDocumentRenderer()
