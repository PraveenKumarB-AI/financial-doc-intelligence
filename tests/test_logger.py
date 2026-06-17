"""
tests/test_logger.py — logging module tests
Writes a test entry and reads it back.
"""
import json
from logs.logger import log_request, read_logs


def test_log_request_writes_entry():
    log_request(
        endpoint="/test_suite",
        status="ok",
        latency_s=0.123,
        question="test question",
        company="Apple Inc.",
    )
    logs = read_logs(n=10)
    endpoints = [l["endpoint"] for l in logs]
    assert "/test_suite" in endpoints


def test_log_entry_has_required_fields():
    log_request(endpoint="/field_check", status="ok", latency_s=0.01)
    logs = read_logs(n=5)
    entry = next((l for l in logs if l["endpoint"] == "/field_check"), None)
    assert entry is not None
    assert "ts" in entry
    assert "endpoint" in entry
    assert "status" in entry
    assert "latency_s" in entry


def test_log_error_status():
    log_request(endpoint="/error_check", status="error", latency_s=0.5,
                error="test error message")
    logs = read_logs(n=5)
    entry = next((l for l in logs if l["endpoint"] == "/error_check"), None)
    assert entry is not None
    assert entry["status"] == "error"
    assert "error" in entry


def test_read_logs_returns_list():
    logs = read_logs(n=10)
    assert isinstance(logs, list)


def test_read_logs_respects_n():
    logs = read_logs(n=3)
    assert len(logs) <= 3
