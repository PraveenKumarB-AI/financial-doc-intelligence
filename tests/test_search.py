"""
tests/test_search.py — vector search tests
All require a loaded DB — skip in CI.
"""
import os
import pytest
from vectorstore.search import search

skip_in_ci = pytest.mark.skipif(
    os.getenv("CI") == "true",
    reason="Requires a database with ingested data; not available in CI"
)


@skip_in_ci
def test_search_returns_results():
    results = search("Apple revenue total net sales")
    assert isinstance(results, list)
    assert len(results) > 0


@skip_in_ci
def test_search_results_are_tuples():
    results = search("Microsoft CEO")
    for row in results:
        assert isinstance(row, tuple)
        assert len(row) >= 1


@skip_in_ci
def test_search_with_company_filter():
    results = search("revenue", company="Apple Inc.")
    assert len(results) > 0


@skip_in_ci
def test_search_company_filter_isolates():
    apple = search("revenue net income", company="Apple Inc.")
    tesla = search("revenue net income", company="Tesla, Inc.")
    apple_texts = [r[0] for r in apple]
    tesla_texts = [r[0] for r in tesla]
    assert apple_texts != tesla_texts


@skip_in_ci
def test_search_unknown_company_returns_empty():
    results = search("revenue", company="Nonexistent Corp XYZ")
    assert results == []