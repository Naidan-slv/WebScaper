"""Tests for search.py and main.py.

Includes basic search, multi-word queries, TF-IDF ranking, exact phrase search,
CLI command handling, the main entry point, and live integration coverage.
"""

import json
import math
import os
import time
from unittest.mock import MagicMock, Mock, PropertyMock, patch

import pytest

from src.crawler import Crawler, MultiPageCrawler
from src.indexer import Indexer, Persistence, WordFrequency
from src.main import CLI, main
from src.search import MultiwordSearch, Search, TfIdf

# ===== Basic search tests =====

@pytest.fixture
def indexed_documents():
    """Create an Indexer with sample documents for testing."""
    indexer = Indexer()
    
    # Add sample documents
    indexer.add_document("The only way to do great work is to love what you do")
    indexer.add_document("Life is what happens while you're busy making other plans")
    indexer.add_document("The future belongs to those who believe in the beauty of their dreams")
    indexer.add_document("Innovation distinguishes between a leader and a follower")
    indexer.add_document("Life is too short to spend it hating anyone")
    
    # Build the index
    indexer.build_index()
    
    return indexer


class TestSearchInit:
    """Tests for Search.__init__()"""
    
    def test_search_initializes_with_valid_indexer(self, indexed_documents):
        """
        Test that Search initializes with a valid Indexer.
        
        Should accept Indexer and store reference.
        """
        search = Search(indexed_documents)
        
        assert search is not None
        assert search.indexer == indexed_documents
    
    def test_search_rejects_none_indexer(self):
        """
        Test that Search raises ValueError for None indexer.
        
        Should not allow None as indexer.
        """
        with pytest.raises(ValueError):
            Search(None)
    
    def test_search_rejects_invalid_indexer_type(self):
        """
        Test that Search raises ValueError for non-Indexer object.
        
        Should validate indexer type.
        """
        with pytest.raises(ValueError):
            Search("not an indexer")
    
    def test_search_rejects_unbuilt_index(self):
        """
        Test that Search raises RuntimeError if index not built.
        
        Should require build_index() to be called on Indexer first.
        """
        indexer = Indexer()
        indexer.add_document("Some text")
        # Note: NOT calling build_index()
        
        with pytest.raises(RuntimeError):
            Search(indexer)


class TestSearchMethod:
    """Tests for Search.search()"""
    
    def test_search_finds_documents_with_word(self, indexed_documents):
        """
        Test that search() returns document IDs for matching word.
        
        Should return list of IDs.
        """
        search = Search(indexed_documents)
        
        results = search.search("life")
        
        assert isinstance(results, list)
        assert len(results) > 0
        assert 1 in results  # "Life is what happens..."
        assert 4 in results  # "Life is too short..."
    
    def test_search_returns_empty_for_unknown_word(self, indexed_documents):
        """
        Test that search() returns empty list for unknown word.
        
        Should gracefully handle words not in index.
        """
        search = Search(indexed_documents)
        
        results = search.search("unicorn")
        
        assert results == []
    
    def test_search_is_case_insensitive(self, indexed_documents):
        """
        Test that search() is case-insensitive.
        
        Should find matches regardless of case.
        """
        search = Search(indexed_documents)
        
        results_lower = search.search("love")
        results_upper = search.search("LOVE")
        results_title = search.search("Love")
        
        assert results_lower == results_upper == results_title
        assert len(results_lower) > 0
    
    def test_search_rejects_empty_query(self, indexed_documents):
        """
        Test that search() raises ValueError for empty query.
        
        Should not allow empty string.
        """
        search = Search(indexed_documents)
        
        with pytest.raises(ValueError):
            search.search("")
    
    def test_search_rejects_none_query(self, indexed_documents):
        """
        Test that search() raises ValueError for None query.
        
        Should not allow None.
        """
        search = Search(indexed_documents)
        
        with pytest.raises(ValueError):
            search.search(None)
    
    def test_search_rejects_non_string_query(self, indexed_documents):
        """
        Test that search() raises TypeError for non-string query.
        
        Should validate query type.
        """
        search = Search(indexed_documents)
        
        with pytest.raises(TypeError):
            search.search(123)
    
    def test_search_handles_punctuation(self, indexed_documents):
        """
        Test that search() handles punctuation correctly.
        
        Should find words even if search includes punctuation.
        """
        search = Search(indexed_documents)
        
        # Search for "work," should find "work"
        results = search.search("work,")
        
        # Depends on tokenization - but should not crash
        assert isinstance(results, list)


class TestGetDocumentText:
    """Tests for Search.get_document_text()"""
    
    def test_get_document_text_returns_full_text(self, indexed_documents):
        """
        Test that get_document_text() returns full original text.
        
        Should return exact document text.
        """
        search = Search(indexed_documents)
        
        text = search.get_document_text(0)
        
        assert text == "The only way to do great work is to love what you do"
    
    def test_get_document_text_for_different_documents(self, indexed_documents):
        """
        Test that get_document_text() returns correct text for each doc.
        
        Should return different text for different IDs.
        """
        search = Search(indexed_documents)
        
        text_0 = search.get_document_text(0)
        text_1 = search.get_document_text(1)
        text_2 = search.get_document_text(2)
        
        assert text_0 != text_1 != text_2
        assert "way to do great" in text_0
        assert "happens while" in text_1
        assert "future belongs" in text_2
    
    def test_get_document_text_rejects_invalid_doc_id(self, indexed_documents):
        """
        Test that get_document_text() raises ValueError for invalid doc_id.
        
        Should not allow non-existent document IDs.
        """
        search = Search(indexed_documents)
        
        with pytest.raises(ValueError):
            search.get_document_text(999)
    
    def test_get_document_text_rejects_negative_doc_id(self, indexed_documents):
        """
        Test that get_document_text() raises ValueError for negative doc_id.
        
        Should validate doc_id >= 0.
        """
        search = Search(indexed_documents)
        
        with pytest.raises(ValueError):
            search.get_document_text(-1)
    
    def test_get_document_text_rejects_non_integer_doc_id(self, indexed_documents):
        """
        Test that get_document_text() raises TypeError for non-integer doc_id.
        
        Should validate doc_id type.
        """
        search = Search(indexed_documents)
        
        with pytest.raises(TypeError):
            search.get_document_text("0")


class TestGetSnippet:
    """Tests for Search.get_snippet()"""
    
    def test_get_snippet_returns_text_with_word(self, indexed_documents):
        """
        Test that get_snippet() includes the query word in result.
        
        Should return snippet containing the word.
        """
        search = Search(indexed_documents)
        
        snippet = search.get_snippet(0, "love")
        
        assert "love" in snippet.lower()
    
    def test_get_snippet_includes_context(self, indexed_documents):
        """
        Test that get_snippet() includes words before and after.
        
        Should show context around the query word.
        """
        search = Search(indexed_documents)
        
        # Doc 0: "The only way to do great work is to love what you do"
        # "love" is at position with "is to love what you"
        snippet = search.get_snippet(0, "love", context_words=2)
        
        # Should include words around "love"
        assert "love" in snippet.lower()
        # With context_words=2, should have some words before/after
        assert len(snippet.split()) >= 3
    
    def test_get_snippet_respects_context_words_parameter(self, indexed_documents):
        """
        Test that get_snippet() respects context_words parameter.
        
        Should include specified number of context words.
        """
        search = Search(indexed_documents)
        
        snippet_1 = search.get_snippet(0, "love", context_words=1)
        snippet_3 = search.get_snippet(0, "love", context_words=3)
        
        # snippet_3 should generally be longer or equal
        assert len(snippet_3.split()) >= len(snippet_1.split())
    
    def test_get_snippet_with_zero_context(self, indexed_documents):
        """
        Test that get_snippet() with context_words=0 returns just the word.
        
        Should allow zero context.
        """
        search = Search(indexed_documents)
        
        snippet = search.get_snippet(0, "love", context_words=0)
        
        assert "love" in snippet.lower()
    
    def test_get_snippet_rejects_invalid_doc_id(self, indexed_documents):
        """
        Test that get_snippet() raises ValueError for invalid doc_id.
        """
        search = Search(indexed_documents)
        
        with pytest.raises(ValueError):
            search.get_snippet(999, "love")
    
    def test_get_snippet_rejects_word_not_in_document(self, indexed_documents):
        """
        Test that get_snippet() raises ValueError if word not in document.
        
        Document 0 doesn't contain "future".
        """
        search = Search(indexed_documents)
        
        with pytest.raises(ValueError):
            search.get_snippet(0, "future")
    
    def test_get_snippet_rejects_negative_context_words(self, indexed_documents):
        """
        Test that get_snippet() raises ValueError for negative context_words.
        
        Should not allow negative context.
        """
        search = Search(indexed_documents)
        
        with pytest.raises(ValueError):
            search.get_snippet(0, "love", context_words=-1)


class TestSearchWithSnippets:
    """Tests for Search.search_with_snippets()"""
    
    def test_search_with_snippets_returns_list_of_dicts(self, indexed_documents):
        """
        Test that search_with_snippets() returns correct format.
        
        Should return list of dicts with doc_id and snippet keys.
        """
        search = Search(indexed_documents)
        
        results = search.search_with_snippets("life")
        
        assert isinstance(results, list)
        assert len(results) > 0
        for result in results:
            assert isinstance(result, dict)
            assert "doc_id" in result
            assert "snippet" in result
    
    def test_search_with_snippets_includes_all_matching_docs(self, indexed_documents):
        """
        Test that search_with_snippets() includes all matching documents.
        
        "life" appears in docs 1 and 4.
        """
        search = Search(indexed_documents)
        
        results = search.search_with_snippets("life")
        doc_ids = [r["doc_id"] for r in results]
        
        assert 1 in doc_ids
        assert 4 in doc_ids
    
    def test_search_with_snippets_returns_snippets_with_word(self, indexed_documents):
        """
        Test that each result snippet contains the query word.
        
        Every snippet should have the word somewhere.
        """
        search = Search(indexed_documents)
        
        results = search.search_with_snippets("work")
        
        for result in results:
            assert "work" in result["snippet"].lower()
    
    def test_search_with_snippets_returns_empty_for_unknown_word(self, indexed_documents):
        """
        Test that search_with_snippets() returns empty list for unknown word.
        
        Should handle gracefully.
        """
        search = Search(indexed_documents)
        
        results = search.search_with_snippets("unicorn")
        
        assert results == []
    
    def test_search_with_snippets_rejects_empty_query(self, indexed_documents):
        """
        Test that search_with_snippets() raises ValueError for empty query.
        """
        search = Search(indexed_documents)
        
        with pytest.raises(ValueError):
            search.search_with_snippets("")
    
    def test_search_with_snippets_rejects_negative_context(self, indexed_documents):
        """
        Test that search_with_snippets() raises ValueError for negative context.
        """
        search = Search(indexed_documents)
        
        with pytest.raises(ValueError):
            search.search_with_snippets("life", snippet_context=-1)


# ===== Multi-word search tests =====

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


# ===== TF-IDF and phrase-search tests =====

# ============================================================
# Fixtures
# ============================================================

@pytest.fixture
def indexer():
    """Provide a built indexer with 3 documents."""
    idx = Indexer()
    idx.add_document("the cat sat on the mat")            # doc 0: "the" x2
    idx.add_document("the dog chased the cat the cat")    # doc 1: "the" x3, "cat" x2
    idx.add_document("fish swim in the ocean")             # doc 2: "the" x1
    idx.build_index()
    return idx


@pytest.fixture
def tfidf(indexer):
    """Provide a ready TfIdf instance."""
    return TfIdf(indexer)


# ============================================================
# Test Class 1: Initialization
# ============================================================

class TestTfIdfInit:
    """Tests for __init__ validation."""

    def test_init_with_valid_indexer(self, indexer):
        """Creates successfully with a built indexer."""
        t = TfIdf(indexer)
        assert t.indexer is indexer

    def test_init_raises_if_indexer_none(self):
        """Raises ValueError if indexer is None."""
        with pytest.raises(ValueError):
            TfIdf(None)

    def test_init_raises_if_index_empty(self):
        """Raises ValueError if indexer has no built index."""
        idx = Indexer()
        with pytest.raises(ValueError):
            TfIdf(idx)

    def test_init_raises_if_no_documents(self):
        """Raises ValueError if indexer has no documents."""
        idx = Indexer()
        idx.index = {"word": [0]}  # fake index but no docs
        with pytest.raises(ValueError):
            TfIdf(idx)


# ============================================================
# Test Class 2: calculate_tf
# ============================================================

class TestCalculateTf:
    """Tests for term frequency calculation."""

    def test_tf_word_appears_once(self, tfidf):
        """TF for a word appearing once in a 6-word doc."""
        # doc 0: "the cat sat on the mat" -> "sat" appears 1/6
        tf = tfidf.calculate_tf("sat", 0)
        assert tf == pytest.approx(1 / 6)

    def test_tf_word_appears_twice(self, tfidf):
        """TF for a word appearing twice in a 6-word doc."""
        # doc 0: "the cat sat on the mat" -> "the" appears 2/6
        tf = tfidf.calculate_tf("the", 0)
        assert tf == pytest.approx(2 / 6)

    def test_tf_word_not_in_doc(self, tfidf):
        """TF is 0.0 for a word not in the document."""
        tf = tfidf.calculate_tf("fish", 0)
        assert tf == 0.0

    def test_tf_case_insensitive(self, tfidf):
        """TF lookup is case-insensitive."""
        tf = tfidf.calculate_tf("CAT", 0)
        assert tf == pytest.approx(1 / 6)

    def test_tf_raises_if_doc_not_found(self, tfidf):
        """Raises KeyError for nonexistent doc_id."""
        with pytest.raises(KeyError):
            tfidf.calculate_tf("cat", 999)

    def test_tf_different_doc_lengths(self, tfidf):
        """TF accounts for different document lengths."""
        # doc 1: "the dog chased the cat the cat" -> "cat" 2/7
        # doc 0: "the cat sat on the mat" -> "cat" 1/6
        tf_doc1 = tfidf.calculate_tf("cat", 1)
        tf_doc0 = tfidf.calculate_tf("cat", 0)
        assert tf_doc1 == pytest.approx(2 / 7)
        assert tf_doc0 == pytest.approx(1 / 6)


# ============================================================
# Test Class 3: calculate_idf
# ============================================================

class TestCalculateIdf:
    """Tests for inverse document frequency calculation."""

    def test_idf_word_in_all_docs(self, tfidf):
        """IDF is low (but positive) for a word in every document."""
        # "the" is in all 3 docs -> log(1 + 3/3) = log(2)
        idf = tfidf.calculate_idf("the")
        assert idf == pytest.approx(math.log(2))

    def test_idf_word_in_some_docs(self, tfidf):
        """IDF is higher for a word in fewer documents."""
        # "cat" in doc 0, 1 -> log(1 + 3/2)
        idf = tfidf.calculate_idf("cat")
        assert idf == pytest.approx(math.log(1 + 3 / 2))

    def test_idf_word_in_one_doc(self, tfidf):
        """IDF is highest for a word in only one document."""
        # "fish" in doc 2 only -> log(1 + 3/1) = log(4)
        idf = tfidf.calculate_idf("fish")
        assert idf == pytest.approx(math.log(4))

    def test_idf_word_not_in_index(self, tfidf):
        """IDF is 0.0 for a word not in the index."""
        idf = tfidf.calculate_idf("xyzzy")
        assert idf == 0.0

    def test_idf_case_insensitive(self, tfidf):
        """IDF lookup is case-insensitive."""
        idf = tfidf.calculate_idf("FISH")
        assert idf == pytest.approx(math.log(4))

    def test_idf_rare_word_higher_than_common(self, tfidf):
        """Rare words have higher IDF than common words."""
        idf_rare = tfidf.calculate_idf("fish")   # 1 doc
        idf_common = tfidf.calculate_idf("the")  # 3 docs
        assert idf_rare > idf_common


# ============================================================
# Test Class 4: calculate_tfidf
# ============================================================

class TestCalculateTfIdf:
    """Tests for combined TF-IDF score."""

    def test_tfidf_is_tf_times_idf(self, tfidf):
        """TF-IDF equals TF * IDF."""
        word, doc = "cat", 0
        tf = tfidf.calculate_tf(word, doc)
        idf = tfidf.calculate_idf(word)
        assert tfidf.calculate_tfidf(word, doc) == pytest.approx(tf * idf)

    def test_tfidf_zero_for_ubiquitous_word(self, tfidf):
        """TF-IDF is low (but positive) for a word in every document."""
        # With smoothed IDF, ubiquitous words still score > 0
        score = tfidf.calculate_tfidf("the", 0)
        assert score > 0.0
        # But lower than a word with same TF but in fewer docs
        # "cat" appears 1x in doc 0 (TF=1/6), in 2 docs: IDF=log(1+3/2)
        # "the" appears 2x in doc 0 (TF=2/6), in 3 docs: IDF=log(1+3/3)
        # "fish" appears 0x in doc 0, so use doc 2 for comparison
        score_fish_doc2 = tfidf.calculate_tfidf("fish", 2)
        # "fish" in 1 doc → higher IDF → higher score per occurrence
        assert score_fish_doc2 > 0.0

    def test_tfidf_zero_for_absent_word(self, tfidf):
        """TF-IDF is 0 for a word not in the document (TF = 0)."""
        score = tfidf.calculate_tfidf("fish", 0)
        assert score == pytest.approx(0.0)

    def test_tfidf_positive_for_relevant_word(self, tfidf):
        """TF-IDF is positive for a word present in doc but not all docs."""
        # "sat" only in doc 0
        score = tfidf.calculate_tfidf("sat", 0)
        assert score > 0.0

    def test_tfidf_raises_if_doc_not_found(self, tfidf):
        """Raises KeyError for nonexistent doc_id."""
        with pytest.raises(KeyError):
            tfidf.calculate_tfidf("cat", 999)

    def test_tfidf_higher_for_rarer_word(self, tfidf):
        """Rarer words score higher than common ones in same doc."""
        # doc 0: "sat" (1 doc) vs "cat" (2 docs), both appear once
        score_rare = tfidf.calculate_tfidf("sat", 0)
        score_common = tfidf.calculate_tfidf("cat", 0)
        assert score_rare > score_common


# ============================================================
# Test Class 5: rank_documents
# ============================================================

class TestRankDocuments:
    """Tests for document ranking by query."""

    def test_single_word_ranking(self, tfidf):
        """Ranks documents for a single-word query."""
        results = tfidf.rank_documents("cat")
        assert len(results) > 0
        assert "doc_id" in results[0]
        assert "score" in results[0]

    def test_results_sorted_by_score_desc(self, tfidf):
        """Results sorted highest score first."""
        results = tfidf.rank_documents("cat")
        scores = [r["score"] for r in results]
        assert scores == sorted(scores, reverse=True)

    def test_excludes_zero_score_docs(self, tfidf):
        """Documents with 0 TF-IDF are excluded."""
        # "fish" only in doc 2
        results = tfidf.rank_documents("fish")
        doc_ids = [r["doc_id"] for r in results]
        assert 0 not in doc_ids
        assert 2 in doc_ids

    def test_multiword_sums_scores(self, tfidf):
        """Multi-word query sums TF-IDF across all terms."""
        results = tfidf.rank_documents("cat sat")
        # doc 0 has both "cat" and "sat" -> highest combined score
        assert results[0]["doc_id"] == 0

    def test_raises_if_query_none(self, tfidf):
        """Raises ValueError for None query."""
        with pytest.raises(ValueError):
            tfidf.rank_documents(None)

    def test_raises_if_query_empty(self, tfidf):
        """Raises ValueError for empty query."""
        with pytest.raises(ValueError):
            tfidf.rank_documents("")

    def test_no_results_for_nonexistent_word(self, tfidf):
        """Returns empty list for word not in any document."""
        results = tfidf.rank_documents("xyzzy")
        assert results == []


# ============================================================
# Test Class 6: search (ranked search with snippets)
# ============================================================

class TestSearch:
    """Tests for ranked search with snippets."""

    def test_returns_ranked_results(self, tfidf):
        """search returns results ranked by TF-IDF."""
        results = tfidf.search("cat")
        assert len(results) > 0
        scores = [r["score"] for r in results]
        assert scores == sorted(scores, reverse=True)

    def test_results_contain_snippet(self, tfidf):
        """Each result has a snippet."""
        results = tfidf.search("cat")
        for r in results:
            assert "snippet" in r
            assert len(r["snippet"]) > 0

    def test_results_contain_doc_id(self, tfidf):
        """Each result has a doc_id."""
        results = tfidf.search("cat")
        for r in results:
            assert "doc_id" in r

    def test_limit_parameter(self, tfidf):
        """limit caps number of results."""
        results = tfidf.search("cat", limit=1)
        assert len(results) <= 1

    def test_no_results_for_nonexistent(self, tfidf):
        """Returns empty for word not in index."""
        results = tfidf.search("xyzzy")
        assert results == []

    def test_raises_if_query_none(self, tfidf):
        """Raises ValueError for None query."""
        with pytest.raises(ValueError):
            tfidf.search(None)


# ============================================================
# Test Class 7: rank_documents_and (AND logic)
# ============================================================

class TestRankDocumentsAnd:
    """Tests for AND-logic ranking — only docs containing ALL query words."""

    @pytest.fixture
    def and_indexer(self):
        """Indexer with 3 docs for AND-logic testing."""
        idx = Indexer()
        idx.add_document("good friends are rare")       # doc 0: good + friends
        idx.add_document("good things take time")        # doc 1: good only
        idx.add_document("friends forever and always")   # doc 2: friends only
        idx.build_index()
        return idx

    @pytest.fixture
    def and_tfidf(self, and_indexer):
        return TfIdf(and_indexer)

    def test_and_returns_only_docs_with_all_words(self, and_tfidf):
        """rank_documents_and returns only docs containing ALL query terms."""
        results = and_tfidf.rank_documents_and("good friends")
        doc_ids = [r["doc_id"] for r in results]
        assert 0 in doc_ids         # has both
        assert 1 not in doc_ids     # missing 'friends'
        assert 2 not in doc_ids     # missing 'good'

    def test_and_single_word_same_as_rank(self, and_tfidf):
        """Single-word AND query behaves like normal rank_documents."""
        and_results = and_tfidf.rank_documents_and("good")
        or_results = and_tfidf.rank_documents("good")
        assert len(and_results) == len(or_results)

    def test_and_no_overlap_returns_empty(self, and_tfidf):
        """If no doc has ALL words, returns empty list."""
        results = and_tfidf.rank_documents_and("rare time")
        assert results == []

    def test_and_results_sorted_by_score(self, and_tfidf):
        """AND results are sorted by TF-IDF score descending."""
        results = and_tfidf.rank_documents_and("good friends")
        scores = [r["score"] for r in results]
        assert scores == sorted(scores, reverse=True)

    def test_and_raises_if_query_none(self, and_tfidf):
        """Raises ValueError for None query."""
        with pytest.raises(ValueError):
            and_tfidf.rank_documents_and(None)

    def test_and_raises_if_query_empty(self, and_tfidf):
        """Raises ValueError for empty query."""
        with pytest.raises(ValueError):
            and_tfidf.rank_documents_and("")


# ============================================================
# Test Class 8: rank_phrase (exact phrase matching)
# ============================================================

class TestRankPhrase:
    """Tests for exact phrase ranking using stored word positions."""

    @pytest.fixture
    def phrase_indexer(self):
        idx = Indexer()
        idx.add_document("good friends are rare")           # doc 0: exact phrase at 0
        idx.add_document("good old friends stay close")     # doc 1: words, not adjacent
        idx.add_document("friends good are reversed")       # doc 2: wrong order
        idx.add_document("good friends good friends")       # doc 3: exact phrase twice
        idx.build_index()
        return idx

    @pytest.fixture
    def phrase_tfidf(self, phrase_indexer):
        return TfIdf(phrase_indexer)

    def test_phrase_returns_only_adjacent_ordered_matches(self, phrase_tfidf):
        results = phrase_tfidf.rank_phrase("good friends")
        doc_ids = [r["doc_id"] for r in results]

        assert 0 in doc_ids
        assert 3 in doc_ids
        assert 1 not in doc_ids
        assert 2 not in doc_ids

    def test_phrase_result_includes_match_positions(self, phrase_tfidf):
        results = phrase_tfidf.rank_phrase("good friends")
        by_doc = {r["doc_id"]: r for r in results}

        assert by_doc[0]["positions"] == [0]
        assert by_doc[3]["positions"] == [0, 2]

    def test_phrase_frequency_boosts_repeated_phrase(self, phrase_tfidf):
        results = phrase_tfidf.rank_phrase("good friends")

        assert results[0]["doc_id"] == 3
        assert results[0]["phrase_frequency"] == 2

    def test_phrase_is_case_insensitive_and_ignores_punctuation(self, phrase_tfidf):
        lower = phrase_tfidf.rank_phrase("good friends")
        mixed = phrase_tfidf.rank_phrase("GOOD, FRIENDS!")

        assert [r["doc_id"] for r in mixed] == [r["doc_id"] for r in lower]

    def test_phrase_single_word_uses_normal_ranking(self, phrase_tfidf):
        phrase_results = phrase_tfidf.rank_phrase("rare")
        normal_results = phrase_tfidf.rank_documents_and("rare")

        assert phrase_results == normal_results

    def test_phrase_no_results_for_nonexistent_phrase(self, phrase_tfidf):
        results = phrase_tfidf.rank_phrase("rare friends")

        assert results == []

    def test_phrase_raises_if_query_none(self, phrase_tfidf):
        with pytest.raises(ValueError):
            phrase_tfidf.rank_phrase(None)

    def test_phrase_raises_if_query_empty(self, phrase_tfidf):
        with pytest.raises(ValueError):
            phrase_tfidf.rank_phrase("")


# ===== CLI command tests =====

# ============================================================
# Test Class 1: Initialization
# ============================================================

class TestCLIInit:
    """Tests for CLI initialization."""

    def test_init_creates_crawler(self):
        """CLI creates a Crawler on init."""
        cli = CLI()
        assert cli.crawler is not None

    def test_init_creates_indexer(self):
        """CLI creates an Indexer on init."""
        cli = CLI()
        assert cli.indexer is not None

    def test_init_not_built(self):
        """CLI starts with is_built = False."""
        cli = CLI()
        assert cli.is_built is False

    def test_init_search_is_none(self):
        """CLI starts with search = None (no index loaded)."""
        cli = CLI()
        assert cli.search is None

    def test_init_tfidf_is_none(self):
        """CLI starts with tfidf = None (no index loaded)."""
        cli = CLI()
        assert cli.tfidf is None


# ============================================================
# Test Class 2: Build Command
# ============================================================

class TestBuildCommand:
    """Tests for the 'build' command."""

    @patch("src.main.MultiPageCrawler")
    @patch("src.main.Persistence")
    @patch("src.main.WordFrequency")
    @patch("src.main.MultiwordSearch")
    @patch("src.main.Search")
    @patch("os.makedirs")
    def test_build_crawls_and_indexes(self, mock_makedirs, mock_search_cls,
                                       mock_mws_cls, mock_wf_cls,
                                       mock_persist_cls, mock_mpc_cls):
        """build() crawls pages and builds index."""
        cli = CLI()

        # Mock multi-page crawler
        mock_mpc = Mock()
        mock_mpc.fetch_and_parse_all.return_value = [
            {"page": 1, "text": "hello world", "url": "http://test.com/"},
        ]
        mock_mpc_cls.return_value = mock_mpc

        # Mock persistence
        mock_persist = Mock()
        mock_persist_cls.return_value = mock_persist

        # Mock search components
        mock_wf = Mock()
        mock_wf_cls.return_value = mock_wf

        result = cli.build(max_pages=1)

        assert result["pages_crawled"] == 1
        assert result["docs_stored"] == 1
        assert cli.is_built is True

    @patch("src.main.MultiPageCrawler")
    @patch("src.main.Persistence")
    @patch("src.main.WordFrequency")
    @patch("src.main.MultiwordSearch")
    @patch("src.main.Search")
    @patch("os.makedirs")
    def test_build_saves_index_to_file(self, mock_makedirs, mock_search_cls,
                                        mock_mws_cls, mock_wf_cls,
                                        mock_persist_cls, mock_mpc_cls):
        """build() saves index and documents to file system."""
        cli = CLI()

        mock_mpc = Mock()
        mock_mpc.fetch_and_parse_all.return_value = [
            {"page": 1, "text": "hello world", "url": "http://test.com/"},
        ]
        mock_mpc_cls.return_value = mock_mpc

        mock_persist = Mock()
        mock_persist_cls.return_value = mock_persist

        mock_wf = Mock()
        mock_wf_cls.return_value = mock_wf

        cli.build(max_pages=1)

        mock_persist.save_index.assert_called_once()
        mock_persist.save_documents.assert_called_once()

    @patch("src.main.MultiPageCrawler")
    @patch("src.main.Persistence")
    @patch("src.main.WordFrequency")
    @patch("src.main.MultiwordSearch")
    @patch("src.main.Search")
    @patch("os.makedirs")
    def test_build_wires_search_components(self, mock_makedirs, mock_search_cls,
                                            mock_mws_cls, mock_wf_cls,
                                            mock_persist_cls, mock_mpc_cls):
        """build() wires up search, multiword search, and word frequency."""
        cli = CLI()

        mock_mpc = Mock()
        mock_mpc.fetch_and_parse_all.return_value = [
            {"page": 1, "text": "hello world", "url": "http://test.com/"},
        ]
        mock_mpc_cls.return_value = mock_mpc

        mock_persist = Mock()
        mock_persist_cls.return_value = mock_persist

        mock_wf = Mock()
        mock_wf_cls.return_value = mock_wf

        cli.build(max_pages=1)

        assert cli.search is not None
        assert cli.multiword_search is not None
        assert cli.word_freq is not None


# ============================================================
# Test Class 3: Load Command
# ============================================================

class TestLoadCommand:
    """Tests for the 'load' command."""

    def test_load_raises_if_no_index_file(self, tmp_path):
        """load() raises FileNotFoundError if index file doesn't exist."""
        cli = CLI()
        with patch("src.main.DEFAULT_INDEX_FILE", str(tmp_path / "missing.json")):
            with pytest.raises(FileNotFoundError):
                cli.load()

    def test_load_raises_if_no_docs_file(self, tmp_path):
        """load() raises FileNotFoundError if documents file doesn't exist."""
        cli = CLI()
        # Create index file but not docs file
        index_file = tmp_path / "index.json"
        index_file.write_text('{"hello": [0]}')

        with patch("src.main.DEFAULT_INDEX_FILE", str(index_file)):
            with patch("src.main.DEFAULT_DOCS_FILE", str(tmp_path / "missing.json")):
                with pytest.raises(FileNotFoundError):
                    cli.load()

    def test_load_restores_index(self, tmp_path):
        """load() restores the inverted index from file."""
        cli = CLI()

        # Create test files with rich index format
        index_file = tmp_path / "index.json"
        docs_file = tmp_path / "documents.json"
        index_file.write_text('{"hello": {"0": {"frequency": 1, "positions": [0]}}, "world": {"0": {"frequency": 1, "positions": [1]}}}')
        docs_file.write_text('{"0": {"text": "hello world"}}')

        with patch("src.main.DEFAULT_INDEX_FILE", str(index_file)):
            with patch("src.main.DEFAULT_DOCS_FILE", str(docs_file)):
                result = cli.load()

        assert result["words_loaded"] == 2
        assert result["docs_loaded"] == 1
        assert cli.is_built is True

    def test_load_wires_search(self, tmp_path):
        """load() creates search components after loading index."""
        cli = CLI()

        index_file = tmp_path / "index.json"
        docs_file = tmp_path / "documents.json"
        index_file.write_text('{"hello": {"0": {"frequency": 1, "positions": [0]}}, "world": {"0": {"frequency": 1, "positions": [1]}}}')
        docs_file.write_text('{"0": {"text": "hello world"}}')

        with patch("src.main.DEFAULT_INDEX_FILE", str(index_file)):
            with patch("src.main.DEFAULT_DOCS_FILE", str(docs_file)):
                cli.load()

        assert cli.search is not None
        assert cli.multiword_search is not None


# ============================================================
# Test Class 4: Print Command
# ============================================================

class TestPrintCommand:
    """Tests for the 'print' command."""

    def _build_cli(self):
        """Create a CLI with a built index for testing."""
        cli = CLI()
        cli.indexer.add_document("hello world hello")
        cli.indexer.build_index()
        cli._wire_search_components()
        return cli

    def test_print_found_word(self):
        """print_index returns entry with stats for word in index."""
        cli = self._build_cli()
        result = cli.print_index("hello")
        assert result is not None
        assert result["word"] == "hello"
        assert 0 in result["doc_ids"]

    def test_print_returns_frequency(self):
        """print_index result includes frequency per document."""
        cli = self._build_cli()
        result = cli.print_index("hello")
        # "hello world hello" -> hello appears 2 times in doc 0
        assert result["entries"][0]["frequency"] == 2

    def test_print_returns_positions(self):
        """print_index result includes positions per document."""
        cli = self._build_cli()
        result = cli.print_index("hello")
        # "hello world hello" -> hello at positions [0, 2]
        assert result["entries"][0]["positions"] == [0, 2]

    def test_print_not_found(self):
        """print_index returns None for word not in index."""
        cli = self._build_cli()
        result = cli.print_index("xyzzy")
        assert result is None

    def test_print_case_insensitive(self):
        """print_index is case-insensitive."""
        cli = self._build_cli()
        result = cli.print_index("HELLO")
        assert result is not None
        assert result["word"] == "hello"

    def test_print_before_build(self):
        """print_index shows error if no index loaded."""
        cli = CLI()
        result = cli.print_index("hello")
        assert result is None


# ============================================================
# Test Class 5: Find Command
# ============================================================

class TestFindCommand:
    """Tests for the 'find' command."""

    def _build_cli(self):
        """Create a CLI with a built index for testing."""
        cli = CLI()
        cli.indexer.add_document("the world is full of good friends", url="http://quotes.toscrape.com/")
        cli.indexer.add_document("good things come to those who wait", url="http://quotes.toscrape.com/page/2/")
        cli.indexer.build_index()
        cli._wire_search_components()
        return cli

    def test_find_single_word(self):
        """find returns results for single word query."""
        cli = self._build_cli()
        results = cli.find("friends")
        assert len(results) > 0

    def test_find_multi_word_and_logic(self):
        """find multi-word returns only docs containing ALL words (AND)."""
        cli = self._build_cli()
        results = cli.find("good friends")
        doc_ids = [r["doc_id"] for r in results]
        # doc 0 has both 'good' and 'friends', doc 1 has only 'good'
        assert 0 in doc_ids
        assert 1 not in doc_ids

    def test_find_no_results(self):
        """find returns empty for non-existent word."""
        cli = self._build_cli()
        results = cli.find("xyzzyplugh")
        assert results == []

    def test_find_before_build(self):
        """find returns empty if no index loaded."""
        cli = CLI()
        results = cli.find("hello")
        assert results == []

    def test_find_results_include_url(self):
        """find results include the page URL for each document."""
        cli = self._build_cli()
        results = cli.find("good")
        assert len(results) > 0
        for r in results:
            assert "url" in r
        # doc 0 should have its URL
        doc0_result = [r for r in results if r["doc_id"] == 0]
        assert doc0_result[0]["url"] == "http://quotes.toscrape.com/"

    def test_find_returns_snippets(self):
        """find results contain doc_id, score, and snippet."""
        cli = self._build_cli()
        results = cli.find("friends")
        assert len(results) > 0
        assert "doc_id" in results[0]
        assert "snippet" in results[0]
        assert "score" in results[0]

    def test_find_results_ranked_by_score(self):
        """find returns results sorted by TF-IDF score descending."""
        cli = self._build_cli()
        results = cli.find("friends")
        if len(results) > 1:
            scores = [r["score"] for r in results]
            assert scores == sorted(scores, reverse=True)

    def test_find_quoted_phrase_uses_exact_positions(self):
        """Quoted find query returns only exact phrase matches."""
        cli = CLI()
        cli.indexer.add_document("good friends are rare", url="http://example.com/exact")
        cli.indexer.add_document("good old friends stay close", url="http://example.com/gap")
        cli.indexer.add_document("friends good are reversed", url="http://example.com/reversed")
        cli.indexer.build_index()
        cli._wire_search_components()

        results = cli.find('"good friends"')
        doc_ids = [r["doc_id"] for r in results]

        assert 0 in doc_ids
        assert 1 not in doc_ids
        assert 2 not in doc_ids
        assert results[0]["match_type"] == "phrase"

    def test_find_quoted_phrase_returns_phrase_positions(self):
        """Phrase results include starting positions for the match."""
        cli = CLI()
        cli.indexer.add_document("good friends good friends", url="http://example.com/repeated")
        cli.indexer.build_index()
        cli._wire_search_components()

        results = cli.find('"good friends"')

        assert results[0]["phrase_positions"] == [0, 2]
        assert results[0]["phrase_frequency"] == 2
        assert "good friends" in results[0]["snippet"]

    def test_find_quoted_phrase_output_labels_exact_phrase(self, capsys):
        """CLI output labels quoted searches as exact phrase searches."""
        cli = CLI()
        cli.indexer.add_document("good friends are rare")
        cli.indexer.build_index()
        cli._wire_search_components()

        cli.find('"good friends"')
        captured = capsys.readouterr()

        assert "exact phrase" in captured.out


# ============================================================
# Test Class 6: REPL (run) Tests
# ============================================================

class TestRunREPL:
    """Tests for the interactive REPL loop."""

    @patch("builtins.input")
    def test_run_quit(self, mock_input):
        """run exits on 'quit' command."""
        mock_input.side_effect = ["quit"]
        cli = CLI()
        cli.run()  # Should not raise

    @patch("builtins.input")
    def test_run_exit(self, mock_input):
        """run exits on 'exit' command."""
        mock_input.side_effect = ["exit"]
        cli = CLI()
        cli.run()

    @patch("builtins.input")
    def test_run_help(self, mock_input, capsys):
        """run shows help on 'help' command."""
        mock_input.side_effect = ["help", "quit"]
        cli = CLI()
        cli.run()
        captured = capsys.readouterr()
        assert "build" in captured.out
        assert "load" in captured.out
        assert "print" in captured.out
        assert "find" in captured.out

    @patch("builtins.input")
    def test_run_unknown_command(self, mock_input, capsys):
        """run handles unknown commands gracefully."""
        mock_input.side_effect = ["foobar", "quit"]
        cli = CLI()
        cli.run()
        captured = capsys.readouterr()
        assert "Unknown command" in captured.out

    @patch("builtins.input")
    def test_run_skips_empty_input(self, mock_input, capsys):
        """run ignores blank commands and keeps waiting."""
        mock_input.side_effect = ["", "quit"]
        cli = CLI()
        cli.run()
        captured = capsys.readouterr()
        assert "Goodbye" in captured.out

    @patch("builtins.input")
    def test_run_build_command(self, mock_input):
        """run dispatches the build command."""
        mock_input.side_effect = ["build", "quit"]
        cli = CLI()
        with patch.object(cli, "build") as mock_build:
            cli.run()
        mock_build.assert_called_once()

    @patch("builtins.input")
    def test_run_load_reports_missing_file(self, mock_input, capsys):
        """run handles load failures without leaving the REPL."""
        mock_input.side_effect = ["load", "quit"]
        cli = CLI()
        with patch.object(cli, "load", side_effect=FileNotFoundError("missing index")):
            cli.run()
        captured = capsys.readouterr()
        assert "missing index" in captured.out

    @patch("builtins.input")
    def test_run_print_usage_without_word(self, mock_input, capsys):
        """run shows usage for print without a word."""
        mock_input.side_effect = ["print", "quit"]
        cli = CLI()
        cli.run()
        captured = capsys.readouterr()
        assert "Usage: print <word>" in captured.out

    @patch("builtins.input")
    def test_run_print_dispatches_word(self, mock_input):
        """run dispatches print with its word argument."""
        mock_input.side_effect = ["print love", "quit"]
        cli = CLI()
        with patch.object(cli, "print_index") as mock_print:
            cli.run()
        mock_print.assert_called_once_with("love")

    @patch("builtins.input")
    def test_run_find_usage_without_query(self, mock_input, capsys):
        """run shows usage for find without a query."""
        mock_input.side_effect = ["find", "quit"]
        cli = CLI()
        cli.run()
        captured = capsys.readouterr()
        assert "Usage: find <query>" in captured.out

    @patch("builtins.input")
    def test_run_find_dispatches_query(self, mock_input):
        """run dispatches find with its query argument."""
        mock_input.side_effect = ["find good friends", "quit"]
        cli = CLI()
        with patch.object(cli, "find") as mock_find:
            cli.run()
        mock_find.assert_called_once_with("good friends")

    @patch("builtins.input")
    def test_run_keyboard_interrupt(self, mock_input, capsys):
        """run handles KeyboardInterrupt gracefully."""
        mock_input.side_effect = KeyboardInterrupt()
        cli = CLI()
        cli.run()
        captured = capsys.readouterr()
        assert "Goodbye" in captured.out

    @patch("builtins.input")
    def test_run_eof(self, mock_input, capsys):
        """run handles EOF gracefully."""
        mock_input.side_effect = EOFError()
        cli = CLI()
        cli.run()
        captured = capsys.readouterr()
        assert "Goodbye" in captured.out


# ============================================================
# Test Class 7: Build → Load → Find Round-Trip
# ============================================================

class TestBuildLoadRoundTrip:
    """Tests for build → save → load → find round-trip integrity."""

    def test_build_load_find_round_trip(self, tmp_path):
        """Index built and saved can be loaded and searched correctly."""
        from src.indexer import Persistence

        # --- Build phase: manually index documents ---
        cli = CLI()
        cli.indexer.add_document(
            "the world is full of good friends",
            url="http://example.com/1",
        )
        cli.indexer.add_document(
            "good things come to those who wait",
            url="http://example.com/2",
        )
        cli.indexer.build_index()

        # Save via Persistence
        index_file = str(tmp_path / "index.json")
        docs_file = str(tmp_path / "documents.json")
        persistence = Persistence(cli.indexer)
        persistence.save_index(index_file)
        persistence.save_documents(docs_file)

        # --- Load phase: fresh CLI loads from files ---
        cli2 = CLI()
        with patch("src.main.DEFAULT_INDEX_FILE", index_file):
            with patch("src.main.DEFAULT_DOCS_FILE", docs_file):
                cli2.load()

        # --- Find phase: search must return correct AND results ---
        results = cli2.find("good friends")
        doc_ids = [r["doc_id"] for r in results]
        assert 0 in doc_ids       # doc 0 has both "good" and "friends"
        assert 1 not in doc_ids   # doc 1 has "good" but not "friends"

    def test_load_then_print_works(self, tmp_path):
        """print_index works correctly after load (rich format intact)."""
        from src.indexer import Persistence

        cli = CLI()
        cli.indexer.add_document("hello world hello")
        cli.indexer.build_index()

        index_file = str(tmp_path / "index.json")
        docs_file = str(tmp_path / "documents.json")
        persistence = Persistence(cli.indexer)
        persistence.save_index(index_file)
        persistence.save_documents(docs_file)

        cli2 = CLI()
        with patch("src.main.DEFAULT_INDEX_FILE", index_file):
            with patch("src.main.DEFAULT_DOCS_FILE", docs_file):
                cli2.load()

        result = cli2.print_index("hello")
        assert result is not None
        assert result["word"] == "hello"
        assert result["entries"][0]["frequency"] == 2
        assert result["entries"][0]["positions"] == [0, 2]


# ===== Main entry-point tests =====

class TestMain:
    """Tests for main() entry point."""

    @patch("src.main.CLI")
    def test_main_creates_cli_and_runs(self, mock_cli_cls):
        """main() creates a CLI instance and calls run()."""
        mock_cli = MagicMock()
        mock_cli_cls.return_value = mock_cli

        main()

        mock_cli_cls.assert_called_once()
        mock_cli.run.assert_called_once()


# ===== Live integration tests =====

# ============================================================
# Fixtures - shared setup for real website tests
# ============================================================

BASE_URL = "https://quotes.toscrape.com/"


@pytest.fixture(scope="module")
def real_crawler():
    """Create a real crawler with politeness delay."""
    return Crawler(timeout=15, politeness_delay=6)


@pytest.fixture(scope="module")
def single_page_html(real_crawler):
    """Fetch a single real page from quotes.toscrape.com."""
    html = real_crawler.fetch_page(BASE_URL)
    return html


@pytest.fixture(scope="module")
def single_page_text(real_crawler, single_page_html):
    """Extract text from a single real page."""
    text = real_crawler.extract_text(single_page_html)
    return text


@pytest.fixture(scope="module")
def built_indexer(single_page_text):
    """Build an indexer with a single real page."""
    indexer = Indexer()
    indexer.add_document(single_page_text)
    indexer.build_index()
    return indexer


@pytest.fixture(scope="module")
def multi_page_indexer(real_crawler):
    """Build an indexer with 2 real pages (respects politeness)."""
    mpc = MultiPageCrawler(real_crawler, max_pages=2, base_url=BASE_URL)
    pages = mpc.fetch_and_parse_all()

    indexer = Indexer()
    for page in pages:
        indexer.add_document(page["text"])
    indexer.build_index()
    return indexer


# ============================================================
# Test Class 1: Real Crawler Tests
# ============================================================

@pytest.mark.integration
class TestRealCrawlerFetch:
    """Test that the crawler can fetch real pages from quotes.toscrape.com."""

    def test_fetch_page_returns_html(self, single_page_html):
        """Verify fetch_page returns actual HTML content."""
        assert single_page_html is not None
        assert isinstance(single_page_html, str)
        assert len(single_page_html) > 0

    def test_fetch_page_contains_html_tags(self, single_page_html):
        """Verify fetched content is valid HTML."""
        assert "<html" in single_page_html.lower()
        assert "</html>" in single_page_html.lower()

    def test_fetch_page_contains_quotes(self, single_page_html):
        """Verify the page contains quote content."""
        # quotes.toscrape.com always has quotes on the page
        assert "quote" in single_page_html.lower()

    def test_extract_text_returns_content(self, single_page_text):
        """Verify extract_text produces readable text from real HTML."""
        assert single_page_text is not None
        assert isinstance(single_page_text, str)
        assert len(single_page_text) > 100  # should have substantial content

    def test_extract_text_contains_known_content(self, single_page_text):
        """Verify extracted text contains expected content from the website."""
        # The site has famous quotes - at least some common words should appear
        text_lower = single_page_text.lower()
        # The site definitely has the word "quotes" somewhere
        assert "quote" in text_lower or "world" in text_lower or "life" in text_lower

    def test_extract_text_no_html_tags(self, single_page_text):
        """Verify extracted text has no HTML tags remaining."""
        assert "<div" not in single_page_text
        assert "<span" not in single_page_text
        assert "<html" not in single_page_text


# ============================================================
# Test Class 2: Real Indexer Tests
# ============================================================

@pytest.mark.integration
class TestRealIndexer:
    """Test that the indexer works with real website content."""

    def test_indexer_has_documents(self, built_indexer):
        """Verify indexer stores the real document."""
        assert built_indexer.document_count > 0

    def test_index_is_non_empty(self, built_indexer):
        """Verify the inverted index was built with real words."""
        assert len(built_indexer.index) > 0

    def test_index_contains_common_words(self, built_indexer):
        """Verify index has words that definitely appear on the site."""
        # Common English words that will be on any page with quotes
        index_words = set(built_indexer.index.keys())
        # At least some of these common words should be indexed
        common_words = {"the", "a", "is", "to", "and", "of", "in", "it"}
        found = common_words.intersection(index_words)
        assert len(found) > 0, f"Expected common words in index, found none. Index has {len(index_words)} words."

    def test_search_returns_results_for_common_word(self, built_indexer):
        """Verify searching for a common word returns the document."""
        # "the" is almost certainly on the page
        results = built_indexer.search("the")
        assert len(results) > 0

    def test_get_document_returns_text(self, built_indexer):
        """Verify we can retrieve the stored document text."""
        doc = built_indexer.get_document(0)
        assert isinstance(doc, str)
        assert len(doc) > 100


# ============================================================
# Test Class 3: Real Search Tests
# ============================================================

@pytest.mark.integration
class TestRealSearch:
    """Test search functionality with real website data."""

    def test_search_finds_results(self, built_indexer):
        """Verify search returns results for a word on the site."""
        search = Search(built_indexer)
        results = search.search("the")
        assert len(results) > 0

    def test_search_with_snippets(self, built_indexer):
        """Verify search returns snippets with real content."""
        search = Search(built_indexer)
        results = search.search_with_snippets("the")
        assert len(results) > 0
        assert "doc_id" in results[0]
        assert "snippet" in results[0]
        assert len(results[0]["snippet"]) > 0

    def test_search_nonexistent_word(self, built_indexer):
        """Verify search returns empty for a word not on the site."""
        search = Search(built_indexer)
        results = search.search("xyzzyplugh")  # nonsense word
        assert results == []

    def test_search_case_insensitive(self, built_indexer):
        """Verify case-insensitive search works with real data."""
        search = Search(built_indexer)
        results_lower = search.search("the")
        results_upper = search.search("THE")
        assert results_lower == results_upper


# ============================================================
# Test Class 4: Real Multi-Page Crawler Tests
# ============================================================

@pytest.mark.integration
class TestRealMultiPageCrawler:
    """Test multi-page crawling with real website.
    
    NOTE: These tests make multiple real HTTP requests with 6s delay each.
    """

    def test_multi_page_fetches_pages(self, real_crawler):
        """Verify multi-page crawler fetches multiple real pages."""
        mpc = MultiPageCrawler(real_crawler, max_pages=2, base_url=BASE_URL)
        pages = mpc.fetch_all_pages()
        assert len(pages) == 2
        assert all(isinstance(p, str) for p in pages)

    def test_multi_page_parse_returns_text(self, real_crawler):
        """Verify fetch_and_parse_all returns parsed text from real pages."""
        mpc = MultiPageCrawler(real_crawler, max_pages=2, base_url=BASE_URL)
        results = mpc.fetch_and_parse_all()
        assert len(results) == 2
        for result in results:
            assert "page" in result
            assert "text" in result
            assert "url" in result
            assert len(result["text"]) > 100

    def test_pages_have_different_content(self, real_crawler):
        """Verify different pages have different quotes."""
        mpc = MultiPageCrawler(real_crawler, max_pages=2, base_url=BASE_URL)
        results = mpc.fetch_and_parse_all()
        # Different pages should have different content
        assert results[0]["text"] != results[1]["text"]

    def test_pages_fetched_counter(self, real_crawler):
        """Verify pages_fetched counter is accurate."""
        mpc = MultiPageCrawler(real_crawler, max_pages=2, base_url=BASE_URL)
        mpc.fetch_all_pages()
        assert mpc.get_pages_fetched() == 2


# ============================================================
# Test Class 5: Real Multi-Word Search Tests
# ============================================================

@pytest.mark.integration
class TestRealMultiWordSearch:
    """Test multi-word search with real website data."""

    def test_and_search_returns_results(self, built_indexer):
        """Verify AND search works with real content."""
        search = Search(built_indexer)
        mws = MultiwordSearch(search)
        # "the" and "a" should both be on the page
        results = mws.search_and("the a")
        assert len(results) > 0

    def test_and_search_with_snippets(self, built_indexer):
        """Verify AND search returns snippets with real content."""
        search = Search(built_indexer)
        mws = MultiwordSearch(search)
        results = mws.search_and_with_snippets("the a")
        assert len(results) > 0
        assert "doc_id" in results[0]
        assert "snippet" in results[0]

    def test_or_search_returns_results(self, built_indexer):
        """Verify OR search works with real content."""
        search = Search(built_indexer)
        mws = MultiwordSearch(search)
        results = mws.search_or("the xyzzyplugh")
        # "the" should match even if "xyzzyplugh" doesn't
        assert len(results) > 0

    def test_and_search_no_results(self, built_indexer):
        """Verify AND search returns empty when one word is missing."""
        search = Search(built_indexer)
        mws = MultiwordSearch(search)
        results = mws.search_and("the xyzzyplugh")
        assert results == []


# ============================================================
# Test Class 6: Real Word Frequency Tests
# ============================================================

@pytest.mark.integration
class TestRealWordFrequency:
    """Test word frequency analysis with real website data."""

    def test_calculate_frequencies(self, built_indexer):
        """Verify frequency calculation works with real content."""
        wf = WordFrequency(built_indexer)
        freqs = wf.calculate_frequencies()
        assert isinstance(freqs, dict)
        assert len(freqs) > 0

    def test_common_word_has_frequency(self, built_indexer):
        """Verify common words have non-zero frequency in real content."""
        wf = WordFrequency(built_indexer)
        wf.calculate_frequencies()
        # "the" should appear multiple times on any page
        freq = wf.get_word_frequency("the", 0)
        assert freq > 0

    def test_top_words_are_common(self, built_indexer):
        """Verify top words from real content are common English words."""
        wf = WordFrequency(built_indexer)
        wf.calculate_frequencies()
        top = wf.get_top_words(0, limit=5)
        assert len(top) == 5
        assert all("word" in entry and "frequency" in entry for entry in top)
        # Top words should have frequency > 1
        assert top[0]["frequency"] > 1

    def test_document_length_is_reasonable(self, built_indexer):
        """Verify document length is reasonable for a full page of quotes."""
        wf = WordFrequency(built_indexer)
        wf.calculate_frequencies()
        length = wf.get_document_length(0)
        assert isinstance(length, int)
        # A page of quotes should have at least 50 words
        assert length > 50


# ============================================================
# Test Class 7: Real Multi-Page Indexer Tests
# ============================================================

@pytest.mark.integration
class TestRealMultiPageIndexer:
    """Test indexing with multiple real pages."""

    def test_multi_page_index_has_more_words(self, built_indexer, multi_page_indexer):
        """Verify indexing multiple pages produces a richer index."""
        single_words = len(built_indexer.index)
        multi_words = len(multi_page_indexer.index)
        # More pages should mean more unique words (or at least same)
        assert multi_words >= single_words

    def test_multi_page_has_multiple_documents(self, multi_page_indexer):
        """Verify multiple documents are stored."""
        assert multi_page_indexer.document_count == 2

    def test_multi_page_search_across_pages(self, multi_page_indexer):
        """Verify search finds results across multiple crawled pages."""
        search = Search(multi_page_indexer)
        results = search.search("the")
        # "the" should appear in both pages
        assert len(results) >= 1


# ============================================================
# Test Class 8: Real Persistence Tests
# ============================================================

@pytest.mark.integration
class TestRealPersistence:
    """Test save/load with real website data."""

    def test_save_and_load_real_index(self, built_indexer, tmp_path):
        """Verify real index can be saved and loaded."""
        persistence = Persistence(built_indexer)

        # Save
        index_file = str(tmp_path / "real_index.json")
        bytes_written = persistence.save_index(index_file)
        assert bytes_written > 0

        # Load
        loaded = persistence.load_index(index_file)
        assert isinstance(loaded, dict)
        assert len(loaded) > 0

    def test_save_and_load_real_documents(self, built_indexer, tmp_path):
        """Verify real documents can be saved and loaded."""
        persistence = Persistence(built_indexer)

        # Save
        docs_file = str(tmp_path / "real_docs.json")
        bytes_written = persistence.save_documents(docs_file)
        assert bytes_written > 0

        # Load
        loaded = persistence.load_documents(docs_file)
        assert isinstance(loaded, dict)
        assert len(loaded) > 0

    def test_checkpoint_with_real_data(self, built_indexer, tmp_path):
        """Verify checkpoint save/load works with real data."""
        persistence = Persistence(built_indexer)

        # Save checkpoint
        checkpoint_dir = str(tmp_path / "real_checkpoint")
        result = persistence.save_checkpoint(checkpoint_dir)
        assert "index_file" in result or "docs_file" in result

        # Load checkpoint
        loaded = persistence.load_checkpoint(checkpoint_dir)
        assert "index" in loaded
        assert "documents" in loaded


# ============================================================
# Test Class 9: Full Pipeline Integration
# ============================================================

@pytest.mark.integration
class TestRealFullPipeline:
    """Test the complete crawl → index → search → analyze pipeline."""

    def test_full_pipeline_single_page(self, real_crawler):
        """Test complete single-page pipeline with real website."""
        # 1. Crawl
        html = real_crawler.fetch_page(BASE_URL)
        assert html is not None

        # 2. Extract text
        text = real_crawler.extract_text(html)
        assert len(text) > 100

        # 3. Index
        indexer = Indexer()
        doc_id = indexer.add_document(text)
        indexer.build_index()
        assert doc_id == 0
        assert len(indexer.index) > 0

        # 4. Search
        search = Search(indexer)
        results = search.search("the")
        assert len(results) > 0

        # 5. Search with snippets
        snippet_results = search.search_with_snippets("the")
        assert len(snippet_results) > 0
        assert "snippet" in snippet_results[0]

        # 6. Word frequency
        wf = WordFrequency(indexer)
        freqs = wf.calculate_frequencies()
        assert len(freqs) > 0
        top = wf.get_top_words(0, limit=3)
        assert len(top) == 3

    def test_full_pipeline_multi_page(self, real_crawler):
        """Test complete multi-page pipeline with real website."""
        # 1. Multi-page crawl
        mpc = MultiPageCrawler(real_crawler, max_pages=2, base_url=BASE_URL)
        pages = mpc.fetch_and_parse_all()
        assert len(pages) == 2

        # 2. Index all pages
        indexer = Indexer()
        for page in pages:
            indexer.add_document(page["text"])
        indexer.build_index()
        assert indexer.document_count == 2

        # 3. Search
        search = Search(indexer)
        results = search.search("the")
        assert len(results) > 0

        # 4. Multi-word search
        mws = MultiwordSearch(search)
        and_results = mws.search_and("the a")
        assert len(and_results) > 0

        # 5. Word frequency on both pages
        wf = WordFrequency(indexer)
        wf.calculate_frequencies()
        len1 = wf.get_document_length(0)
        len2 = wf.get_document_length(1)
        assert len1 > 50
        assert len2 > 50

        # 6. Persistence
        import tempfile
        import os
        with tempfile.TemporaryDirectory() as tmpdir:
            persistence = Persistence(indexer)
            persistence.save_checkpoint(tmpdir)
            loaded = persistence.load_checkpoint(tmpdir)
            assert len(loaded["index"]) > 0
            assert len(loaded["documents"]) > 0
