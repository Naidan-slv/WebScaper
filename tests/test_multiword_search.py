"""
Tests for MultiwordSearch class.

Tests cover all 7 methods:
- __init__: Validation of search dependency
- search_and: AND logic across documents
- search_and_with_snippets: AND search with context snippets
- search_or: OR logic across documents
- get_intersection: Set intersection of result sets
- get_union: Set union of result sets
- tokenize_query: Query string tokenization
"""

import pytest
from src.indexer import Indexer
from src.search import Search
from src.search import MultiwordSearch


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture
def built_search():
    """Provide a Search with a built index of 3 documents."""
    indexer = Indexer()
    indexer.add_document("the world is full of good friends")       # doc 0
    indexer.add_document("good things come to those who wait")       # doc 1
    indexer.add_document("the best things in life are free")         # doc 2
    indexer.build_index()
    return Search(indexer)


@pytest.fixture
def mws(built_search):
    """Provide a ready MultiwordSearch instance."""
    return MultiwordSearch(built_search)


# ============================================================
# Test Class 1: Initialization
# ============================================================

class TestMultiwordSearchInit:
    """Tests for __init__ validation."""

    def test_init_with_valid_search(self, built_search):
        """Creates successfully with a valid built Search."""
        mws = MultiwordSearch(built_search)
        assert mws.search is built_search

    def test_init_raises_if_search_none(self):
        """Raises ValueError if search is None."""
        with pytest.raises(ValueError, match="None"):
            MultiwordSearch(None)

    def test_init_raises_if_search_missing_indexer(self):
        """Raises RuntimeError if search has no indexer attribute."""
        fake_search = object()
        with pytest.raises(RuntimeError):
            MultiwordSearch(fake_search)

    def test_init_raises_if_indexer_not_built(self):
        """Raises RuntimeError if search.indexer has empty index."""
        indexer = Indexer()
        search = Search(indexer)
        with pytest.raises(RuntimeError):
            MultiwordSearch(search)


# ============================================================
# Test Class 2: tokenize_query
# ============================================================

class TestTokenizeQuery:
    """Tests for tokenize_query method."""

    def test_single_word(self, mws):
        """Single word returns list with one element."""
        assert mws.tokenize_query("hello") == ["hello"]

    def test_multiple_words(self, mws):
        """Multiple words split into list."""
        assert mws.tokenize_query("good friends") == ["good", "friends"]

    def test_lowercases_input(self, mws):
        """Words are lowercased."""
        assert mws.tokenize_query("HELLO World") == ["hello", "world"]

    def test_strips_whitespace(self, mws):
        """Leading/trailing whitespace stripped."""
        assert mws.tokenize_query("  good  friends  ") == ["good", "friends"]

    def test_raises_if_none(self, mws):
        """Raises ValueError if query is None."""
        with pytest.raises(ValueError, match="None"):
            mws.tokenize_query(None)

    def test_raises_if_empty(self, mws):
        """Raises ValueError if query is empty."""
        with pytest.raises(ValueError, match="empty"):
            mws.tokenize_query("")

    def test_raises_if_whitespace_only(self, mws):
        """Raises ValueError if query is whitespace only."""
        with pytest.raises(ValueError, match="empty"):
            mws.tokenize_query("   ")


# ============================================================
# Test Class 3: get_intersection
# ============================================================

class TestGetIntersection:
    """Tests for get_intersection method."""

    def test_single_set(self, mws):
        """Single set returns itself."""
        result = mws.get_intersection([[0, 1, 2]])
        assert result == {0, 1, 2}

    def test_two_overlapping_sets(self, mws):
        """Returns common elements from two sets."""
        result = mws.get_intersection([[0, 1, 2], [1, 2, 3]])
        assert result == {1, 2}

    def test_no_overlap(self, mws):
        """Returns empty set if no overlap."""
        result = mws.get_intersection([[0, 1], [2, 3]])
        assert result == set()

    def test_empty_input(self, mws):
        """Returns empty set for empty input."""
        result = mws.get_intersection([])
        assert result == set()

    def test_three_sets(self, mws):
        """Intersection of three sets."""
        result = mws.get_intersection([[0, 1, 2], [1, 2, 3], [2, 3, 4]])
        assert result == {2}

    def test_one_empty_set(self, mws):
        """Empty set in input makes intersection empty."""
        result = mws.get_intersection([[0, 1, 2], []])
        assert result == set()


# ============================================================
# Test Class 4: get_union
# ============================================================

class TestGetUnion:
    """Tests for get_union method."""

    def test_single_set(self, mws):
        """Single set returns itself."""
        result = mws.get_union([[0, 1, 2]])
        assert result == {0, 1, 2}

    def test_two_overlapping_sets(self, mws):
        """Returns all unique elements from two sets."""
        result = mws.get_union([[0, 1], [1, 2]])
        assert result == {0, 1, 2}

    def test_no_overlap(self, mws):
        """Returns all elements when no overlap."""
        result = mws.get_union([[0, 1], [2, 3]])
        assert result == {0, 1, 2, 3}

    def test_empty_input(self, mws):
        """Returns empty set for empty input."""
        result = mws.get_union([])
        assert result == set()

    def test_one_empty_set(self, mws):
        """Empty set doesn't affect union."""
        result = mws.get_union([[0, 1], []])
        assert result == {0, 1}


# ============================================================
# Test Class 5: search_and
# ============================================================

class TestSearchAnd:
    """Tests for search_and (AND logic)."""

    def test_both_words_in_one_doc(self, mws):
        """Returns doc containing both words."""
        # "good" in doc 0, 1; "friends" in doc 0 only
        results = mws.search_and("good friends")
        assert 0 in results

    def test_no_common_docs(self, mws):
        """Returns empty when no doc has all words."""
        # "friends" in doc 0; "free" in doc 2
        results = mws.search_and("friends free")
        assert results == []

    def test_single_word_query(self, mws):
        """Single word falls back to basic search."""
        results = mws.search_and("good")
        assert 0 in results
        assert 1 in results

    def test_all_words_in_all_docs(self, mws):
        """Returns all docs when all share the words."""
        # "the" is in doc 0 and doc 2
        results = mws.search_and("the")
        assert 0 in results
        assert 2 in results

    def test_raises_if_query_none(self, mws):
        """Raises ValueError if query is None."""
        with pytest.raises(ValueError):
            mws.search_and(None)

    def test_returns_sorted(self, mws):
        """Results are sorted by doc_id."""
        results = mws.search_and("the")
        assert results == sorted(results)


# ============================================================
# Test Class 6: search_or
# ============================================================

class TestSearchOr:
    """Tests for search_or (OR logic)."""

    def test_union_of_two_words(self, mws):
        """Returns docs containing either word."""
        # "friends" in doc 0; "free" in doc 2
        results = mws.search_or("friends free")
        assert 0 in results
        assert 2 in results

    def test_single_word(self, mws):
        """Single word returns same as basic search."""
        results = mws.search_or("friends")
        assert results == [0]

    def test_nonexistent_words(self, mws):
        """Returns empty for words not in index."""
        results = mws.search_or("xyzzy plugh")
        assert results == []

    def test_raises_if_query_none(self, mws):
        """Raises ValueError if query is None."""
        with pytest.raises(ValueError):
            mws.search_or(None)

    def test_returns_sorted(self, mws):
        """Results are sorted by doc_id."""
        results = mws.search_or("friends free good")
        assert results == sorted(results)

    def test_or_returns_more_than_and(self, mws):
        """OR always returns >= AND results."""
        and_results = mws.search_and("friends free")
        or_results = mws.search_or("friends free")
        assert len(or_results) >= len(and_results)


# ============================================================
# Test Class 7: search_and_with_snippets
# ============================================================

class TestSearchAndWithSnippets:
    """Tests for search_and_with_snippets."""

    def test_returns_results_with_snippets(self, mws):
        """Results contain doc_id, snippet, and text keys."""
        results = mws.search_and_with_snippets("good friends")
        assert len(results) >= 1
        assert "doc_id" in results[0]
        assert "snippet" in results[0]
        assert "text" in results[0]

    def test_snippet_contains_query_word(self, mws):
        """Snippet includes at least one query word."""
        results = mws.search_and_with_snippets("good friends")
        assert len(results) >= 1
        snippet = results[0]["snippet"].lower()
        assert "good" in snippet or "friends" in snippet

    def test_no_results_for_nonexistent(self, mws):
        """Returns empty for words not in index."""
        results = mws.search_and_with_snippets("xyzzy plugh")
        assert results == []

    def test_raises_if_query_none(self, mws):
        """Raises ValueError if query is None."""
        with pytest.raises(ValueError):
            mws.search_and_with_snippets(None)

    def test_doc_id_matches_and_search(self, mws):
        """Snippet results have same doc_ids as search_and."""
        and_ids = mws.search_and("good friends")
        snippet_ids = [r["doc_id"] for r in mws.search_and_with_snippets("good friends")]
        assert and_ids == snippet_ids
