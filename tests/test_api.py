"""Smoke tests for the API service."""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    return TestClient(app, raise_server_exceptions=False)


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_process_requires_auth(client):
    resp = client.post(
        "/process",
        json={
            "booking_excel_s3_key": "uploads/u/x/bookings.xlsx",
            "confirmation_pdf_s3_key": "uploads/u/x/confirms.pdf",
        },
    )
    assert resp.status_code in (401, 403)


def test_upload_urls_requires_auth(client):
    resp = client.get("/upload-urls", params={"filenames": "bookings.xlsx"})
    assert resp.status_code in (401, 403)
