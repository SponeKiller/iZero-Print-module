# Adding a document
This document will describe how to add a new document do Print Module 

## 1. Domain Layer
Separate document on components
Validates data - dtype, length, required ... 

`app/domain/delivery_notes/entities/`

- One entity per part of the document (`DeliveryNote`, `DeliveryItem`,
  ...), built through `create`, which calls `_validate` and then the
  constructor. No `update` - a print request is never changed.
- `_validate` checks only the values supplied by the caller, with the
  functions of `app/domain/shared/validation.py`
  (`validate_text(number=number, max_length=20)`). The keyword is the
  reported field.
- An entity never builds or checks other entities or value objects; it
  gets them already built.
- Reuse the shared value objects (`Address`, `CompanyId`, `VatId`,
  `Iban`). A new value object is a frozen dataclass validated in
  `__post_init__`.

## 2. Application - DTOs and formatting

`app/application/dto/delivery_note/` - one file per entity, each with
`<Entity>In` (as supplied) and `<Entity>Out` (every value as the printed
text, `str` or `None`), plus `print_delivery_note.py` with
`PrintDeliveryNoteOut(filename, content, document_format)`.

`app/application/use_cases/delivery_notes/format_delivery_note.py` -
`FormatDeliveryNote.execute(note) -> DeliveryNoteOut`. All formatting is
here (numbers, dates, ...), templates never format. Keep the formats of
`FormatInvoice`.

## 3. Application - components, variants, labels, design

In `app/application/constants/templates/`, one file per entity in each
folder:

| Folder | Add |
|--------|-----|
| `variants/` | `DeliveryNoteVariant(StrEnum)` - the layouts (`CLASSIC = "classic"`), and a variant enum for every new child |
| `labels/` | `DeliveryNoteLabel(StrEnum)` - every fixed text it prints (`TITLE = "Dodací list"`) |
| `components/` | `DeliveryNoteComponent` - frozen dataclass with `name: ClassVar[str] = "delivery_note"`, `labels`, `variant` and one attribute per child component |
| `design/` | `DeliveryNoteDesign(Enum)` - `CLASSIC = DocumentComponent(variant=DocumentVariant.STANDARD, content=DeliveryNoteComponent(...))` |

Children that already exist (`SupplierComponent`, `AddressComponent`,
...) are reused - add only what the document does not share. The
document type (`DocumentVariant.STANDARD`) brings the page, header and
footer; add a new `DocumentVariant` only for a different page style.

## 4. Application - the print use case

`app/application/use_cases/delivery_notes/print_delivery_note.py` -
copy `PrintInvoice`:

1. Build the domain objects from the DTO inside
   `try: ... except DomainValidationError as e: raise InvalidDocumentDataError(e.problem) from e`.
2. `FormatDeliveryNote().execute(note)`.
3. `self.template_engine.fill(DeliveryNoteDesign.CLASSIC.value, formatted)`.
4. `self.document_renderer.render(document, DocumentFormat.PDF)`.
5. Return `PrintDeliveryNoteOut(filename=f"delivery-note-{note.number}.pdf", ...)`.

No try/except around steps 2-4 - their failures go to the global handler.
The ports and adapters stay as they are.

## 5. Templates

In the templates directory (`app/infrastructure/templates`), one folder
per component and one set of files per variant:

```
templates/delivery_note/
├── classic.html.jinja       layout: areas on the paper, render(child, data.child)
├── classic.css.jinja        sizes of the areas from dimensions
└── classic.dimensions.json  needs, slots, rows, gap_mm
```

- The parent places its children: `{{ render(component.supplier, data.supplier) }}`
  and includes their styles with `{{ style(component.supplier) }}`.
- Texts only from labels (`{{ labels.TITLE }}`), values only from data
  (`{{ data.number }}`). No filters, no formatting, no literal texts.
- Leave optional values out when they are `None`
  (`{% if data.vat_id %}`).
- Sizes come from `dimensions`, never written twice.

## 6. API

| File | Add |
|------|-----|
| `app/infrastructure/api/schemas/delivery_note/` | Pydantic schemas mirroring the DTO files (`DeliveryNoteSchemaIn`, ...) - shape, types, required |
| `app/infrastructure/api/endpoints/delivery_note/__init__.py` | `router = build_aggregate_router(__file__, __package__, prefix="/delivery-notes", tags=["delivery_note"])` |
| `app/infrastructure/api/endpoints/delivery_note/print_delivery_note.py` | `POST /print`: schema -> DTO, run the use case, return `Response` with the PDF and `Content-Disposition: inline; filename*=UTF-8''{quote(result.filename, safe='')}` |
| `app/infrastructure/api/router.py` | `router.include_router(delivery_note.router)` |

`InvalidDocumentDataError` is already mapped to 422 `PRINT_INVALID_DATA`
in `app/infrastructure/api/errors/`; a new application error needs its
own `MessageId` (`30xxxxx`) and mapping.

## 7. Tests

Every layer of the document gets its tests. Rules for all of them:

- Every test file holds its own data - no shared test data module. A
  test checks the values it defined itself.
- The in-memory fakes of the ports are shared by all documents:
  `tests/support/fake_template_engine.py` and
  `tests/support/fake_document_renderer.py`. Both remember what they were
  given and raise the `error` passed to them, if any.
- Tests that print a real PDF need Chromium and fail without it - they
  are never skipped.
- No test needs a database.
- Run everything with `pytest`, one folder with `pytest tests/visual`.

### E2E

`tests/e2e/delivery_note/test_print_delivery_note.py` - the HTTP contract through
FastAPI `TestClient`, the renderer replaced by `FakeDocumentRenderer` through
`app.dependency_overrides` (copy `tests/e2e/invoice/test_print_invoice.py`):

- 200: `Content-Type: application/pdf`, `Content-Disposition` with the
  percent-encoded file name, the real template filled with the data
- 422 `PRINT_INVALID_DATA`: invalid value (one problem from the domain),
  missing value or part, wrong type, body that is not JSON - always as
  `{code, field, message}`, nothing rendered
- 500 `SYSTEM_INTERNAL_FAIL`: failing template engine or renderer
- one end-to-end test with the real renderer

### Unit

One folder per layer, the tests of one document in its own subfolder
(`tests/unit/<layer>/delivery_note/`):

| Folder | Test file | What it checks |
|--------|-----------|----------------|
| `tests/unit/domain/delivery_note` | `test_delivery_note.py` | Every rule of every entity rejects an invalid value (`field`, `code`) and accepts the boundary values; the first rejected value stops the entity. New value objects go to `tests/unit/domain/test_value_objects.py`. |
| `tests/unit/application/delivery_note` | `test_format_delivery_note.py` | Every value is formatted to its printed text (money, numbers, dates); optional values stay `None`; nothing is validated. |
| `tests/unit/application/delivery_note` | `test_print_delivery_note.py` | The order of steps with `FakeTemplateEngine` and `FakeDocumentRenderer` from `tests/support/`: valid data is formatted, filled with the design and rendered as PDF; invalid data raises `InvalidDocumentDataError` and nothing is filled; port failures are not caught; the file name. |
| `tests/unit/infrastructure/delivery_note` | `test_jinja_template_engine.py` | The real templates with formatted data (`<Entity>Out` built in the test, not through the format use case): every value and label is printed, optional values are left out. |
| `tests/unit/infrastructure` | `test_component_dimensions.py` (shared) | Add `DeliveryNoteDesign` - checks without rendering that every child fits its slot and the slots fit the page. |

The Chromium renderer is shared by all documents and already tested in
`test_chromium_document_renderer.py`.

### Visual

`tests/visual/delivery_note/` - one test file per printed PDF, for a few
typical cases (`test_complete_delivery_note.py`,
`test_delivery_note_without_optional_values.py`,
`test_delivery_note_over_several_pages.py`). Each file holds its data,
prints it with the real adapters and calls
`assert_pdf_looks_like(pdf, __file__)` from `tests/visual/compare_pdf.py`.

The approved images are named after the test file: `images/<test file>.png`,
or `images/<test file>_page_<n>.png` for every page of a longer document.
A new test fails until its approved images, rendered on Linux, are there.

## 8. Documentation

- Technical documentation of the document in Notion (Document Hub, type
  `Documentation`, linked to its analysis).
- Add the endpoint to the README.
