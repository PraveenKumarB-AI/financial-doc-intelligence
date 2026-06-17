"""
tests/test_api.py — API endpoint tests
Uses FastAPI's TestClient — no real server needed, runs instantly.
"""
from fastapi.testclient import TestClient
from api.app import app

client = TestClient(app)


def test_home():
    r = client.get("/")
    assert r.status_code == 200
    assert "message" in r.json()


def test_stats_returns_200():
    r = client.get("/stats")
    assert r.status_code == 200


def test_stats_has_required_keys():
    r = client.get("/stats")
    data = r.json()
    for key in ["total_companies", "total_filings", "total_chunks", "last_updated"]:
        assert key in data, f"Missing key: {key}"


def test_stats_companies_is_three():
    r = client.get("/stats")
    assert r.json()["total_companies"] == 3


def test_stats_chunks_nonzero():
    r = client.get("/stats")
    assert r.json()["total_chunks"] > 0


def test_companies_returns_200():
    r = client.get("/companies")
    assert r.status_code == 200


def test_companies_has_three():
    r = client.get("/companies")
    data = r.json()
    assert "companies" in data
    assert len(data["companies"]) == 3


def test_companies_contains_expected():
    r = client.get("/companies")
    names = r.json()["companies"]
    assert "Apple Inc." in names
    assert "Microsoft Corporation" in names
    assert "Tesla, Inc." in names


def test_metrics_returns_200():
    r = client.get("/metrics")
    assert r.status_code == 200


def test_metrics_has_data():
    r = client.get("/metrics")
    data = r.json()
    assert "metrics" in data
    assert len(data["metrics"]) > 0


def test_metrics_company_filter():
    r = client.get("/metrics?company=Apple Inc.")
    data = r.json()
    for row in data["metrics"]:
        assert row["company"] == "Apple Inc."


def test_metrics_row_shape():
    r = client.get("/metrics")
    row = r.json()["metrics"][0]
    for key in ["company", "fiscal_year", "metric", "value"]:
        assert key in row, f"Missing key: {key}"


def test_logs_returns_200():
    r = client.get("/logs")
    assert r.status_code == 200


def test_logs_has_logs_key():
    r = client.get("/logs")
    assert "logs" in r.json()


def test_logs_n_param():
    r = client.get("/logs?n=2")
    assert r.status_code == 200
    data = r.json()
    assert len(data["logs"]) <= 2
