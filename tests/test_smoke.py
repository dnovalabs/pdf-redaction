"""Smoke tests — enough to gate CI before build + deploy."""

from fastapi.testclient import TestClient

from app import app

client = TestClient(app)


def test_index_serves_html():
    resp = client.get("/")
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]


def test_healthz_ok():
    resp = client.get("/healthz")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_metrics_exposed():
    resp = client.get("/metrics")
    assert resp.status_code == 200
