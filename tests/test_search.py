"""
tests/test_search.py — vector search tests
Requires the DB to be running with data loaded.
Skip gracefully if DB is unavailable.
"""
import pytest
from vectorstore.search import search


def test_search_returns_results():
    results = search("Apple revenue total net sales")
    assert isinstance(results, list)
    assert len(results) > 0


def test_search_results_are_tuples():
    results = search("Microsoft CEO")
    for row in results:
        assert isinstance(row, tuple)
        assert len(row) >= 1


def test_search_with_company_filter():
    results = search("revenue", company="Apple Inc.")
    assert len(results) > 0
    

def test_search_company_filter_isolates():
    apple = search("revenue net income", company="Apple Inc.")
    tesla = search("revenue net income", company="Tesla, Inc.")
    apple_texts = [r[0] for r in apple]
    tesla_texts = [r[0] for r in tesla]
    assert apple_texts != tesla_texts


def test_search_unknown_company_returns_empty():
    results = search("revenue", company="Nonexistent Corp XYZ")
    assert results == []
