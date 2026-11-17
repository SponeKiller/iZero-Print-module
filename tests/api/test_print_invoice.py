from contextlib import contextmanager
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.infrastructure.api.dependencies.printing import (
    get_document_renderer,
    get_template_engine,
)
from app.infrastructure.api.main import app
from app.infrastructure.api.middleware import http_audit
from app.infrastructure.api.schemas.message_id import MessageId
from tests.shared.fake_document_renderer import FakeDocumentRenderer
from tests.shared.fake_template_engine import FakeTemplateEngine

URL = "/api/invoices/print"


def invoice_json() -> dict[str, Any]:
    """Valid invoice data as the JSON body of the print endpoint."""
    return {
        "number": "2026-0042",
        "issue_date": "2026-11-02",
        "supplier": {
            "name": "Dodavatel s.r.o.",
            "company_id": "12345678",
            "vat_id": "CZ12345678",
            "address": {
                "street": "Dlouhá 12",
                "city": "Praha",
                "postal_code": "110 00",
                "country": "Česká republika",
            },
        },
        "customer": {
            "name": "Odběratel a.s.",
            "address": {
                "street": "Krátká 3",
                "city": "Brno",
                "postal_code": "602 00",
                "country": "Česká republika",
            },
        },
        "items": [
            {
                "description": "Konzultace",
                "quantity": "2.5",
                "unit": "h",
                "unit_price": 1200,
                "vat_rate": 21,
                "total": "3630.00",
            },
        ],
        "payments": {
            "iban": "CZ6508000000192000145399",
            "amount_to_pay": "3630.00",
            "currency": "CZK",
            "variable_symbol": "20260042",
            "due_date": "2026-11-16",
        },
    }


@contextmanager
def _no_database():
    raise RuntimeError("tests run without a database")
    yield


@pytest.fixture(autouse=True)
def without_audit_database(monkeypatch):
    # The audit middleware swallows its own failures - make it fail fast
    # instead of trying to reach PostgreSQL.
    monkeypatch.setattr(http_audit, "db_session", _no_database)


@pytest.fixture
def renderer():
    return FakeDocumentRenderer()


@pytest.fixture
def client(renderer):
    app.dependency_overrides[get_document_renderer] = lambda: renderer
    with TestClient(app, raise_server_exceptions=False) as client:
        yield client
    app.dependency_overrides.clear()


def test_valid_invoice_is_returned_as_pdf(client, renderer):
    response = client.post(URL, json=invoice_json())

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.headers["content-disposition"] == (
        "inline; filename*=UTF-8''invoice-2026-0042.pdf"
    )
    assert response.content.startswith(b"%PDF-fake ")
    # the real template was filled with the supplied data
    assert "2026-0042" in renderer.rendered[0]
    assert "CZ65 0800 0000 1920 0014 5399" in renderer.rendered[0]


def test_file_name_is_encoded_in_the_header(client):
    body = invoice_json()
    body["number"] = 'FV/2026 "42"'

    response = client.post(URL, json=body)

    assert response.status_code == 200
    assert response.headers["content-disposition"] == (
        "inline; filename*=UTF-8''invoice-FV%2F2026%20%2242%22.pdf"
    )


def test_invalid_data_returns_the_problem_and_prints_nothing(
    client, renderer
):
    body = invoice_json()
    body["customer"]["address"]["city"] = "x" * 101
    body["items"][0]["quantity"] = "12345678.901"

    response = client.post(URL, json=body)

    # The first invalid object rejects the data
    assert response.status_code == 422
    assert response.json() == {
        "message_id": MessageId.PRINT_INVALID_DATA,
        "message": None,
        "data": [
            {
                "code": "too_long",
                "field": "city",
                "message": "Must have at most 100 characters.",
            },
        ],
    }
    assert renderer.rendered == []


def test_missing_required_values_are_rejected(client, renderer):
    body = invoice_json()
    del body["number"]
    del body["customer"]["address"]["city"]
    del body["items"][0]["quantity"]
    del body["payments"]["due_date"]

    response = client.post(URL, json=body)

    assert response.status_code == 422
    assert [
        (problem["field"], problem["code"])
        for problem in response.json()["data"]
    ] == [
        ("number", "required"),
        ("customer.address.city", "required"),
        ("items[0].quantity", "required"),
        ("payments.due_date", "required"),
    ]
    assert renderer.rendered == []


def test_missing_parts_of_the_invoice_are_rejected(client, renderer):
    body = invoice_json()
    del body["supplier"]["address"]
    del body["customer"]
    body["items"] = []
    del body["payments"]

    response = client.post(URL, json=body)

    assert response.status_code == 422
    assert response.json()["message_id"] == MessageId.PRINT_INVALID_DATA
    assert [
        (problem["field"], problem["code"])
        for problem in response.json()["data"]
    ] == [
        ("supplier.address", "required"),
        ("customer", "required"),
        ("items", "required"),
        ("payments", "required"),
    ]
    assert renderer.rendered == []


def test_wrong_data_types_are_reported_in_the_same_format(client, renderer):
    body = invoice_json()
    body["number"] = 42
    body["issue_date"] = "2. 11. 2026"
    body["items"][0]["quantity"] = "two"

    response = client.post(URL, json=body)

    assert response.status_code == 422
    assert response.json()["message_id"] == MessageId.PRINT_INVALID_DATA
    assert [
        (problem["field"], problem["code"])
        for problem in response.json()["data"]
    ] == [
        ("number", "invalid_type"),
        ("issue_date", "invalid_type"),
        ("items[0].quantity", "invalid_type"),
    ]
    assert renderer.rendered == []


def test_body_that_is_not_json_is_rejected(client):
    response = client.post(
        URL,
        content=b"{not json",
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 422
    assert [
        (problem["field"], problem["code"])
        for problem in response.json()["data"]
    ] == [("", "invalid_format")]


def test_missing_body_is_rejected(client):
    response = client.post(URL)

    assert response.status_code == 422
    assert [
        (problem["field"], problem["code"])
        for problem in response.json()["data"]
    ] == [("", "required")]


def test_template_failure_is_an_internal_error(client):
    app.dependency_overrides[get_template_engine] = lambda: (
        FakeTemplateEngine(error=RuntimeError("template is broken"))
    )

    response = client.post(URL, json=invoice_json())

    assert response.status_code == 500
    assert response.json() == {
        "message_id": MessageId.SYSTEM_INTERNAL_FAIL,
        "message": None,
        "data": None,
    }


def test_rendering_failure_is_an_internal_error(client):
    app.dependency_overrides[get_document_renderer] = lambda: (
        FakeDocumentRenderer(error=OSError("cannot load library"))
    )

    response = client.post(URL, json=invoice_json())

    assert response.status_code == 500
    assert response.json() == {
        "message_id": MessageId.SYSTEM_INTERNAL_FAIL,
        "message": None,
        "data": None,
    }


def test_end_to_end_with_the_real_renderer():
    with TestClient(app) as client:
        response = client.post(URL, json=invoice_json())

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content.startswith(b"%PDF-")
