# iZero Print Module

Printing service of iZero. The caller sends the data of a document, the
service validates it, fills the document template and returns a PDF. The
first supported document is the invoice. The service has no business logic
of its own and stores no documents.

- How the project works: [docs/overview.md](docs/overview.md)
- Adding another document: [docs/adding-a-document.md](docs/adding-a-document.md)
- Design of the module: [Print Module - Technical documentation](https://app.notion.com/p/41b249716045817088bcf38846ee9f3e) (Notion)
- Rules of the service skeleton: [architecture](docs/architecture.md),
  [naming conventions](docs/naming-conventions.md), [API](docs/api.md),
  [errors and responses](docs/errors-and-responses.md),
  [observability](docs/observability.md)

## API

`POST /api/invoices/print` - JSON with the invoice data in, PDF out.
Invalid data ends with `422` and the first validation problem. See section 6 of the
[technical documentation](https://app.notion.com/p/41b249716045817088bcf38846ee9f3e) for the request and the responses, or Swagger at `http://127.0.0.1:8000/docs`.

The service has **no authentication** - it must only be reachable from the
internal network (BR-7).

## Running in Docker

```powershell
docker build -t izero-print-module .
docker run --env-file .env -p 8000:8000 izero-print-module
```

The entrypoint waits for Postgres (used by the HTTP audit log only), runs
`alembic upgrade head`, the seed and then uvicorn.

## Running locally

Requires Python 3.12+ (the code uses PEP 695 generics; Docker and CI run
3.13) and PostgreSQL. Create `.env` from `.env.dist`.

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
alembic upgrade head
uvicorn app.infrastructure.api.main:app --reload
```

PDF rendering uses headless Chromium through Playwright. After installing
the packages download it once:

```powershell
playwright install --only-shell chromium
```

Without it the service starts, validation works, but printing ends with
`SYSTEM_INTERNAL_FAIL`, and the tests that print a real PDF fail. The
Docker image has it.

## Tests and lint

```powershell
pytest
ruff check .
```

Tests need no database, but they need Chromium (see above) - tests that
print a real PDF fail without it. They can also be run in the image:

```powershell
docker run --rm --user root -v "${PWD}:/work:ro" -w /work --entrypoint sh izero-print-module -c "pip install -q -r requirements-dev.txt && pytest -p no:cacheprovider"
```

### Visual tests

`tests/visual/<document>/` holds one test file per printed PDF. Every
page is compared pixel by pixel with its approved image, named after the
test file (`tests/visual/compare_pdf.py`):

```
tests/visual/invoice/
├── test_complete_invoice.py
└── images/
    ├── test_complete_invoice.png                 one page
    └── test_invoice_over_several_pages_page_1.png  more pages: _page_<n>
```

Pages are rendered with pypdfium2 and compared in gray scale with
Pillow; a page fails when a single pixel differs by more than 5 (of
255). The rendering scale and the difference are in
`tests/visual/config.py`.

The tests only compare and write nothing. A test fails when a page has
no approved image, has a different size or a pixel differs (the message
names the page, the largest difference and the area of the differing
pixels, in pixels from the top left corner), or when an approved image
belongs to a page the PDF no longer has.

Fonts differ between operating systems, so the approved images are
rendered on Linux, like in CI.

CI runs ruff and the single-Alembic-head check (`lint.yml`) and the tests
(`test.yml`) on every pull request to `main`.

## Adding another document

See [docs/adding-a-document.md](docs/adding-a-document.md).
