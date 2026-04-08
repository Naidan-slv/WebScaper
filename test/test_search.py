"""
Tests for the Search class - Step 4: Single-word search functionality.

Tests cover:
- Initialization with Indexer
- Single-word search returning document IDs
- Document text retrieval
- Snippet generation with context
- Search with snippets combined
- Error handling for all methods
"""

import pytest
from src.search import Search
from src.indexer import Indexer


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
