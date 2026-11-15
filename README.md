# iZero Print Module

Printing service of iZero. The caller sends the data of a document, the
service validates it, fills the document template and returns a PDF. The
first supported document is the invoice. The service has no business logic
of its own and stores no documents.

- Design of the module: [docs/print-module.md](docs/print-module.md)
- Rules of the service skeleton: [docs/architecture.md](docs/architecture.md)

## API

`POST /api/invoices/print` - JSON with the invoice data in, PDF out.
Invalid data ends with `422` and the first validation problem. See
[docs/print-module.md](docs/print-module.md#6-api) for the request and the
responses, or Swagger at `http://127.0.0.1:8000/docs`.

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

PDF rendering uses WeasyPrint, which needs the native Pango libraries.
The Docker image has them. On Windows without them the service starts,
validation works, but printing ends with `PRINT_RENDERING_FAILED` - use
Docker, or install Pango
([WeasyPrint installation](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#windows)).

## Tests and lint

```powershell
pytest
ruff check .
```

Tests need no database. Tests that render a real PDF are skipped where
Pango is missing; to run all of them use the image:

```powershell
docker run --rm --user root -v "${PWD}:/work:ro" -w /work --entrypoint sh izero-print-module -c "pip install -q pytest==9.2.0 httpx==0.28.1 && pytest -p no:cacheprovider"
```

CI runs ruff and the single-Alembic-head check (`lint.yml`) and the tests
(`test.yml`) on every pull request to `main`.

## Adding another document type

1. Entities with `create` + `_validate` and value objects in
   `app/domain/<context>/`
2. Template port in `app/application/ports/` and DTOs + use case next to
   `PrintInvoice`
3. Components, variants, labels and the design in
   `app/application/constants/templates/`, the template files in the
   templates directory (`TEMPLATES_DIR`) and the adapter in
   `app/infrastructure/services/`
4. Schemas, endpoint and error mapping in `app/infrastructure/api/`
