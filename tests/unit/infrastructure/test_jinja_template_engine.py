from dataclasses import replace

import pytest
from jinja2 import TemplateNotFound, UndefinedError

from app.application.constants.templates.design.invoice import (
    InvoiceDesign,
)
from app.application.constants.templates.labels.customer import CustomerLabel
from app.application.constants.templates.labels.footer import FooterLabel
from app.application.constants.templates.labels.invoice import InvoiceLabel
from app.application.constants.templates.labels.invoice_item import (
    InvoiceItemLabel,
)
from app.application.constants.templates.labels.payments import PaymentsLabel
from app.application.constants.templates.labels.supplier import SupplierLabel
from app.application.dto.invoice.invoice import InvoiceOut
from app.application.dto.shared.document import DocumentOut
from app.infrastructure.config import settings
from app.infrastructure.services.jinja_template_engine import (
    JinjaTemplateEngine,
)
from tests.support import (
    formatted_invoice,
    item,
    item_without_unit_and_vat,
    payments,
    supplier,
)

NBSP = "\u00a0"

DOCUMENT = InvoiceDesign.CLASSIC.value
# the invoice inside the document
CLASSIC = DOCUMENT.content


def fill(invoice: InvoiceOut) -> str:
    return JinjaTemplateEngine(settings.templates_dir).fill(
        DOCUMENT,
        DocumentOut(title=f"Faktura {invoice.number}", content=invoice),
    )


def write_templates(directory, files: dict[str, str]) -> None:
    for name, content in files.items():
        (directory / name).parent.mkdir(exist_ok=True)
        (directory / name).write_text(content, encoding="utf-8")


def test_fills_every_supplied_value():
    html = fill(formatted_invoice())

    for expected in [
        "Faktura 2026-0042",
        "Dodavatel s.r.o.",
        "Dlouhá 12",
        "110 00 Praha",
        "IČO: 12345678",
        "DIČ: CZ12345678",
        "Odběratel a.s.",
        "602 00 Brno",
        f"2.{NBSP}11.{NBSP}2026",
        f"16.{NBSP}11.{NBSP}2026",
        "CZ65 0800 0000 1920 0014 5399",
        "20260042",
        "Konzultace",
        "2,5",
        f"1{NBSP}200,00",
        "21&nbsp;%",
        f"3{NBSP}630,00",
        "Licence",
        f"1{NBSP}234{NBSP}567,50",
        f"1{NBSP}238{NBSP}197,50&nbsp;CZK",
    ]:
        assert expected in html


def test_leaves_out_optional_values_that_were_not_supplied():
    html = fill(
        formatted_invoice(
            supplier=supplier(vat_id=None),
            payments=payments(variable_symbol=None),
            items=[item_without_unit_and_vat()],
        )
    )

    assert "DIČ" not in html
    assert "Variabilní symbol" not in html
    assert "&nbsp;%" not in html
    assert "None" not in html
    # the customer has neither a company ID nor a VAT ID
    assert html.count("IČO:") == 1


def test_escapes_supplied_values():
    html = fill(
        formatted_invoice(
            supplier=supplier(name="<script>alert(1)</script>"),
            items=[item(description='<img src="http://evil.test/x">')],
        )
    )

    assert "<script>" not in html
    assert "<img" not in html
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html


def test_prints_the_labels_of_every_template():
    html = fill(formatted_invoice())

    for labels in [
        FooterLabel,
        InvoiceLabel,
        SupplierLabel,
        CustomerLabel,
        InvoiceItemLabel,
        PaymentsLabel,
    ]:
        for label in labels:
            assert label in html


def test_includes_the_styles_of_the_children():
    html = fill(formatted_invoice())

    for selector in [".supplier .name", ".customer .name", ".item td",
                     ".payments .total"]:
        assert selector in html


def test_header_and_footer_are_fixed_by_the_type_of_the_document():
    assert DOCUMENT.header.variant == "none"
    assert DOCUMENT.footer.variant == "page_numbers"


def test_document_decides_the_page_and_places_the_content(tmp_path):
    write_templates(
        tmp_path,
        {
            "document/standard.html.jinja": (
                "<style>{{ style(component) }}"
                "{{ style(component.header, data) }}"
                "{{ style(component.footer, data) }}</style>"
                "[{{ render(component.content, data.content) }}]"
            ),
            "document/standard.css.jinja": "@page { margin: 1mm }",
            "footer/page_numbers.css.jinja": (
                '@page { @bottom-left { content: "{{ data.title }} '
                '{{ labels.PAGE }}" } }'
            ),
            "invoice/classic.html.jinja": "{{ data.number }}",
        },
    )

    # the header variant `none` has no file and prints nothing
    assert JinjaTemplateEngine(tmp_path).fill(
        DOCUMENT, DocumentOut(title="Doc", content=formatted_invoice())
    ) == (
        "<style>@page { margin: 1mm }"
        '@page { @bottom-left { content: "Doc Strana" } }</style>'
        "[2026-0042]"
    )


def test_templates_and_styles_get_the_dimensions_of_the_component(tmp_path):
    write_templates(
        tmp_path,
        {
            "invoice/classic.html.jinja": (
                "<style>{{ style(component.supplier) }}</style>"
                "{{ dimensions.gap_mm }}"
            ),
            "invoice/classic.dimensions.json": '{"gap_mm": 10}',
            "supplier/plain.css.jinja": (
                "{{ dimensions.needs.max_height_mm }}mm"
            ),
            "supplier/plain.dimensions.json": (
                '{"needs": {"max_height_mm": 45}}'
            ),
        },
    )

    assert JinjaTemplateEngine(tmp_path).fill(
        CLASSIC, formatted_invoice()
    ) == "<style>45mm</style>10"


def test_page_and_areas_are_sized_by_the_dimensions():
    html = fill(formatted_invoice())

    for expected in [
        "size: 210mm 297mm;",
        "gap: 10mm;",
        ".area-supplier { width: 84mm; }",
        ".area-customer { width: 84mm; }",
    ]:
        assert expected in html


def test_parent_places_its_children_and_design_chooses_their_variant(
    tmp_path,
):
    write_templates(
        tmp_path,
        {
            "invoice/classic.html.jinja": (
                "<style>{{ style(component.supplier) }}</style>"
                "[{{ render(component.supplier, data.supplier) }}]"
            ),
            "supplier/plain.html.jinja": (
                "plain {{ data.name }} "
                "({{ render(component.address, data.address) }})"
            ),
            "supplier/boxed.html.jinja": "boxed {{ data.name }}",
            "supplier/boxed.css.jinja": ".boxed { border: 1pt solid }",
            "address/lines.html.jinja": "{{ data.city }}",
        },
    )
    engine = JinjaTemplateEngine(tmp_path)
    # "boxed" is a variant that exists only in the files of this test
    boxed = replace(
        CLASSIC, supplier=replace(CLASSIC.supplier, variant="boxed")
    )

    assert engine.fill(CLASSIC, formatted_invoice()) == (
        "<style></style>[plain Dodavatel s.r.o. (Praha)]"
    )
    assert engine.fill(boxed, formatted_invoice()) == (
        "<style>.boxed { border: 1pt solid }</style>[boxed Dodavatel s.r.o.]"
    )


def test_missing_template_file_is_an_error(tmp_path):
    with pytest.raises(TemplateNotFound):
        JinjaTemplateEngine(tmp_path).fill(CLASSIC, formatted_invoice())


def test_missing_place_in_the_data_is_an_error(tmp_path):
    write_templates(
        tmp_path, {"invoice/classic.html.jinja": "{{ data.no_such_field }}"}
    )

    with pytest.raises(UndefinedError):
        JinjaTemplateEngine(tmp_path).fill(CLASSIC, formatted_invoice())


def test_missing_label_is_an_error(tmp_path):
    write_templates(
        tmp_path, {"invoice/classic.html.jinja": "{{ labels.NO_SUCH_LABEL }}"}
    )

    with pytest.raises(UndefinedError):
        JinjaTemplateEngine(tmp_path).fill(CLASSIC, formatted_invoice())
