"""
Comprehensive tests for MultiwordSearch class.

Tests cover:
- Multi-word AND query logic
- Multi-word OR query logic
- Set operations (intersection, union)
- Query tokenization
- Snippet generation for multi-word results
- Error handling
"""

import pytest
from unittest.mock import Mock, MagicMock
from src.multiword_search import MultiwordSearch


class TestMultiwordSearchInit:
    """Tests for MultiwordSearch initialization."""

    def test_init_with_valid_search(self):
        """MultiwordSearch initializes with valid Search instance."""
        search = Mock()
        search.indexer = Mock()
        search.indexer.index = {"word": [1]}
        
        mws = MultiwordSearch(search)
        
        assert mws.search == search

    def test_init_raises_error_if_search_none(self):
        """MultiwordSearch raises ValueError if search is None."""
        with pytest.raises(ValueError):
            MultiwordSearch(None)

    def test_init_raises_error_if_search_not_built(self):
        """MultiwordSearch raises RuntimeError if Search not built."""
        search = Mock()
        search.indexer = Mock()
        search.indexer.index = {}  # Empty index
        
        with pytest.raises(RuntimeError):
            MultiwordSearch(search)


class TestTokenizeQuery:
    """Tests for query tokenization."""

    @pytest.fixture
    def mws_setup(self):
        """Provide MultiwordSearch instance."""
        search = Mock()
        search.indexer = Mock()
        search.indexer.index = {"love": [1], "life": [2]}
        return MultiwordSearch(search)

    def test_tokenize_query_splits_words(self, mws_setup):
        """tokenize_query splits query into words."""
        result = mws_setup.tokenize_query("love life wisdom")
        
        assert result == ["love", "life", "wisdom"]

    def test_tokenize_query_lowercases(self, mws_setup):
        """tokenize_query converts to lowercase."""
        result = mws_setup.tokenize_query("LOVE LIFE")
        
        assert result == ["love", "life"]

    def test_tokenize_query_handles_whitespace(self, mws_setup):
        """tokenize_query handles extra whitespace."""
        result = mws_setup.tokenize_query("  love    life  ")
        
        assert result == ["love", "life"]

    def test_tokenize_query_raises_error_if_query_none(self, mws_setup):
        """tokenize_query raises ValueError if query is None."""
        with pytest.raises(ValueError):
            mws_setup.tokenize_query(None)

    def test_tokenize_query_raises_error_if_query_empty(self, mws_setup):
        """tokenize_query raises ValueError if query is empty."""
        with pytest.raises(ValueError):
            mws_setup.tokenize_query("")

    def test_tokenize_query_returns_list(self, mws_setup):
        """tokenize_query returns list of strings."""
        result = mws_setup.tokenize_query("love life")
        
        assert isinstance(result, list)
        assert all(isinstance(word, str) for word in result)


class TestGetIntersection:
    """Tests for set intersection (AND logic)."""

    @pytest.fixture
    def mws_setup(self):
        """Provide MultiwordSearch instance."""
        search = Mock()
        search.indexer = Mock()
        search.indexer.index = {"love": [1, 2], "life": [2, 3]}
        return MultiwordSearch(search)

    def test_get_intersection_returns_common_elements(self, mws_setup):
        """get_intersection returns docs in all sets."""
        result_sets = [[1, 2, 3], [2, 3, 4], [2, 5]]
        
        result = mws_setup.get_intersection(result_sets)
        
        assert result == {2}

    def test_get_intersection_returns_empty_if_no_common(self, mws_setup):
        """get_intersection returns empty set if no common elements."""
        result_sets = [[1, 2], [3, 4], [5, 6]]
        
        result = mws_setup.get_intersection(result_sets)
        
        assert result == set()

    def test_get_intersection_handles_single_set(self, mws_setup):
        """get_intersection handles single set."""
        result_sets = [[1, 2, 3]]
        
        result = mws_setup.get_intersection(result_sets)
        
        assert result == {1, 2, 3}

    def test_get_intersection_handles_empty_sets(self, mws_setup):
        """get_intersection handles empty result sets."""
        result_sets = [[], [1, 2], [3, 4]]
        
        result = mws_setup.get_intersection(result_sets)
        
        assert result == set()


class TestGetUnion:
    """Tests for set union (OR logic)."""

    @pytest.fixture
    def mws_setup(self):
        """Provide MultiwordSearch instance."""
        search = Mock()
        search.indexer = Mock()
        search.indexer.index = {"love": [1, 2], "life": [2, 3]}
        return MultiwordSearch(search)

    def test_get_union_returns_all_elements(self, mws_setup):
        """get_union returns docs in any set."""
        result_sets = [[1, 2], [3, 4], [2, 5]]
        
        result = mws_setup.get_union(result_sets)
        
        assert result == {1, 2, 3, 4, 5}

    def test_get_union_handles_empty_sets(self, mws_setup):
        """get_union handles empty result sets."""
        result_sets = [[], [1, 2], []]
        
        result = mws_setup.get_union(result_sets)
        
        assert result == {1, 2}

    def test_get_union_handles_all_empty(self, mws_setup):
        """get_union handles all empty sets."""
        result_sets = [[], [], []]
        
        result = mws_setup.get_union(result_sets)
        
        assert result == set()

    def test_get_union_handles_single_set(self, mws_setup):
        """get_union handles single set."""
        result_sets = [[1, 2, 3]]
        
        result = mws_setup.get_union(result_sets)
        
        assert result == {1, 2, 3}


class TestSearchAnd:
    """Tests for AND logic search."""

    @pytest.fixture
    def mws_setup(self):
        """Provide MultiwordSearch with mocked Search."""
        search = Mock()
        search.indexer = Mock()
        search.indexer.index = {"love": [1, 2], "life": [2, 3]}
        
        # Mock search_query to return doc IDs
        def mock_search(word):
            if word == "love":
                return [{"doc_id": 1}, {"doc_id": 2}]
            elif word == "life":
                return [{"doc_id": 2}, {"doc_id": 3}]
            return []
        
        search.search_query = Mock(side_effect=mock_search)
        return MultiwordSearch(search)

    def test_search_and_returns_common_docs(self, mws_setup):
        """search_and returns docs containing all words."""
        result = mws_setup.search_and("love life")
        
        assert result == [2]

    def test_search_and_returns_empty_if_no_match(self, mws_setup):
        """search_and returns empty if no doc has all words."""
        result = mws_setup.search_and("love notfound")
        
        assert result == []

    def test_search_and_handles_single_word(self, mws_setup):
        """search_and works with single word (returns that word's docs)."""
        result = mws_setup.search_and("love")
        
        assert result == [1, 2]

    def test_search_and_raises_error_if_query_none(self, mws_setup):
        """search_and raises ValueError if query is None."""
        with pytest.raises(ValueError):
            mws_setup.search_and(None)

    def test_search_and_raises_error_if_query_empty(self, mws_setup):
        """search_and raises ValueError if query is empty."""
        with pytest.raises(ValueError):
            mws_setup.search_and("")


class TestSearchOr:
    """Tests for OR logic search."""

    @pytest.fixture
    def mws_setup(self):
        """Provide MultiwordSearch with mocked Search."""
        search = Mock()
        search.indexer = Mock()
        search.indexer.index = {"love": [1, 2], "life": [2, 3]}
        
        def mock_search(word):
            if word == "love":
                return [{"doc_id": 1}, {"doc_id": 2}]
            elif word == "life":
                return [{"doc_id": 2}, {"doc_id": 3}]
            return []
        
        search.search_query = Mock(side_effect=mock_search)
        return MultiwordSearch(search)

    def test_search_or_returns_all_matching_docs(self, mws_setup):
        """search_or returns docs containing any word."""
        result = mws_setup.search_or("love life")
        
        assert set(result) == {1, 2, 3}

    def test_search_or_removes_duplicates(self, mws_setup):
        """search_or removes duplicate doc IDs."""
        result = mws_setup.search_or("love life")
        
        # Check that 2 appears only once (not twice)
        assert result.count(2) == 1

    def test_search_or_handles_single_word(self, mws_setup):
        """search_or works with single word."""
        result = mws_setup.search_or("love")
        
        assert result == [1, 2]

    def test_search_or_raises_error_if_query_none(self, mws_setup):
        """search_or raises ValueError if query is None."""
        with pytest.raises(ValueError):
            mws_setup.search_or(None)


class TestSearchAndWithSnippets:
    """Tests for AND search with snippets."""

    @pytest.fixture
    def mws_setup(self):
        """Provide MultiwordSearch with mocked Search."""
        search = Mock()
        search.indexer = Mock()
        search.indexer.index = {"love": [1, 2], "life": [2, 3]}
        
        def mock_search(query):
            if query == "love":
                return [{"doc_id": 1}, {"doc_id": 2}]
            elif query == "life":
                return [{"doc_id": 2}, {"doc_id": 3}]
            return []
        
        search.search_query = Mock(side_effect=mock_search)
        search.get_document_text = Mock(return_value="full text here")
        search.get_snippet = Mock(return_value="snippet with love context")
        return MultiwordSearch(search)

    def test_search_and_with_snippets_returns_formatted_results(self, mws_setup):
        """search_and_with_snippets returns results with snippets."""
        result = mws_setup.search_and_with_snippets("love life")
        
        assert len(result) > 0
        assert "doc_id" in result[0]
        assert "snippet" in result[0]

    def test_search_and_with_snippets_respects_context_words(self, mws_setup):
        """search_and_with_snippets uses context_words parameter when getting snippet."""
        mws_setup.search_and_with_snippets("love life", context_words=10)
        
        # Verify get_snippet was called with context_words parameter
        assert mws_setup.search.get_snippet.called
        # Check that it was called with context_words=10
        call_args = mws_setup.search.get_snippet.call_args
        assert call_args[0][2] == 10  # Third argument is context_words

    def test_search_and_with_snippets_raises_error_if_query_invalid(self, mws_setup):
        """search_and_with_snippets raises ValueError if query invalid."""
        with pytest.raises(ValueError):
            mws_setup.search_and_with_snippets(None)

    def test_search_and_with_snippets_returns_empty_if_no_match(self, mws_setup):
        """search_and_with_snippets returns empty if no matching docs."""
        # Mock search_query to return no results for both words
        mws_setup.search.search_query = Mock(return_value=[])
        
        result = mws_setup.search_and_with_snippets("love life")
        
        assert result == []


class TestMultiwordSearchIntegration:
    """Integration tests for multi-word search."""

    def test_full_and_search_workflow(self):
        """Full workflow: tokenize → search each word → intersect."""
        search = Mock()
        search.indexer = Mock()
        search.indexer.index = {"love": [1, 2, 3], "life": [2, 3, 4], "wisdom": [3, 5]}
        
        def mock_search(word):
            results = {
                "love": [{"doc_id": 1}, {"doc_id": 2}, {"doc_id": 3}],
                "life": [{"doc_id": 2}, {"doc_id": 3}, {"doc_id": 4}],
                "wisdom": [{"doc_id": 3}, {"doc_id": 5}]
            }
            return results.get(word, [])
        
        search.search_query = Mock(side_effect=mock_search)
        mws = MultiwordSearch(search)
        
        result = mws.search_and("love life wisdom")
        
        # Only doc 3 has all three words
        assert result == [3]

    def test_full_or_search_workflow(self):
        """Full workflow: tokenize → search each word → union."""
        search = Mock()
        search.indexer = Mock()
        search.indexer.index = {"love": [1, 2], "life": [3, 4]}
        
        def mock_search(word):
            results = {
                "love": [{"doc_id": 1}, {"doc_id": 2}],
                "life": [{"doc_id": 3}, {"doc_id": 4}]
            }
            return results.get(word, [])
        
        search.search_query = Mock(side_effect=mock_search)
        mws = MultiwordSearch(search)
        
        result = mws.search_or("love life")
        
        assert set(result) == {1, 2, 3, 4}

    def test_multiword_vs_single_word_difference(self):
        """Verify AND search is more restrictive than OR."""
        search = Mock()
        search.indexer = Mock()
        search.indexer.index = {"love": [1, 2], "life": [2, 3]}
        
        def mock_search(word):
            results = {
                "love": [{"doc_id": 1}, {"doc_id": 2}],
                "life": [{"doc_id": 2}, {"doc_id": 3}]
            }
            return results.get(word, [])
        
        search.search_query = Mock(side_effect=mock_search)
        mws = MultiwordSearch(search)
        
        and_result = mws.search_and("love life")
        or_result = mws.search_or("love life")
        
        # AND should have fewer/equal results than OR
        assert len(and_result) <= len(or_result)
        # Specifically, AND should be [2], OR should be [1,2,3]
        assert and_result == [2]
        assert set(or_result) == {1, 2, 3}
