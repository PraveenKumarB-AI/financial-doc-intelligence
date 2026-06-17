"""
tests/test_company_detector.py — company detection logic tests
Fast — no DB, no LLM, pure string matching.
"""
from analytics.company_detector import detect_company


def test_detects_apple():
    assert detect_company("Who is the CEO of Apple?") == "Apple Inc."


def test_detects_microsoft():
    assert detect_company("What is Microsoft's revenue?") == "Microsoft Corporation"


def test_detects_tesla():
    assert detect_company("Who founded Tesla?") == "Tesla, Inc."


def test_case_insensitive():
    assert detect_company("APPLE earnings") == "Apple Inc."
    assert detect_company("microsoft cloud") == "Microsoft Corporation"


def test_unknown_returns_none():
    assert detect_company("What is the weather today?") is None


def test_unknown_company_returns_none():
    assert detect_company("Tell me about Samsung and Sony") is None
