"""
Tests for the Indexer class - Rich inverted index with frequency + positions.

Tests:
- test_indexer_initializes_empty: Empty index at startup?
- test_indexer_adds_document: Can add single document?
- test_indexer_builds_inverted_index: Creates word -> {doc_id: {frequency, positions}} mapping?
- test_indexer_stores_word_frequency: Frequency count per doc?
- test_indexer_stores_word_positions: Position list per doc?
- test_indexer_finds_documents_with_word: Can find docs by keyword?
- test_indexer_returns_empty_for_unknown_word: Returns empty for unknown word?
- test_indexer_handles_duplicate_words_in_doc: Deduplicates doc IDs in search?
- test_indexer_is_case_insensitive: Case-insensitive search?
- test_indexer_get_index_entry: Retrieve full stats for a word?
"""

import pytest
from src.indexer import Indexer


class TestIndexer:
    """Test suite for Indexer class."""
    
    # ========== BASIC FUNCTIONALITY TESTS ==========
    
    def test_indexer_initializes_empty(self):
        """
        Test that Indexer initializes with empty index.
        
        Should start with no documents or words indexed.
        """
        indexer = Indexer()
        
        assert indexer.index == {}
        assert indexer.document_count == 0
    
    def test_indexer_adds_single_document(self):
        """
        Test that Indexer can add a single document.
        
        Should accept document text and store it with an ID.
        """
        indexer = Indexer()
        doc_id = indexer.add_document("The only way to do great work is to love what you do")
        
        assert doc_id == 0
        assert indexer.document_count == 1
    
    def test_indexer_adds_multiple_documents(self):
        """
        Test that Indexer can add multiple documents.
        
        Should assign incrementing IDs to each document.
        """
        indexer = Indexer()
        doc_id_1 = indexer.add_document("First quote about success")
        doc_id_2 = indexer.add_document("Second quote about life")
        doc_id_3 = indexer.add_document("Third quote about dreams")
        
        assert doc_id_1 == 0
        assert doc_id_2 == 1
        assert doc_id_3 == 2
        assert indexer.document_count == 3
    
    def test_indexer_builds_inverted_index_simple(self):
        """
        Test that Indexer builds rich inverted index with stats.
        
        Should create mapping: word -> {doc_id: {frequency, positions}}
        """
        indexer = Indexer()
        indexer.add_document("love work")
        indexer.add_document("work hard")
        indexer.build_index()
        
        # Check index structure - words exist
        assert "love" in indexer.index
        assert "work" in indexer.index
        assert "hard" in indexer.index
        
        # Check new dict structure: each word maps to dict of doc entries
        assert isinstance(indexer.index["love"], dict)
        assert isinstance(indexer.index["work"], dict)
        
        # Check doc IDs are keys in the nested dict
        assert 0 in indexer.index["love"]
        assert 0 in indexer.index["work"]
        assert 1 in indexer.index["work"]
        assert 1 in indexer.index["hard"]
        
        # Each doc entry has frequency and positions
        assert "frequency" in indexer.index["love"][0]
        assert "positions" in indexer.index["love"][0]
    
    def test_indexer_stores_word_frequency(self):
        """
        Test that index stores correct word frequency per document.
        
        "love love work" -> love: {0: {frequency: 2, ...}}
        """
        indexer = Indexer()
        indexer.add_document("love love work")
        indexer.build_index()
        
        assert indexer.index["love"][0]["frequency"] == 2
        assert indexer.index["work"][0]["frequency"] == 1
    
    def test_indexer_stores_word_positions(self):
        """
        Test that index stores correct word positions per document.
        
        "love work love" -> love: {0: {positions: [0, 2]}}
        """
        indexer = Indexer()
        indexer.add_document("love work love")
        indexer.build_index()
        
        assert indexer.index["love"][0]["positions"] == [0, 2]
        assert indexer.index["work"][0]["positions"] == [1]
    
    def test_indexer_frequency_across_documents(self):
        """
        Test frequency is tracked per document independently.
        
        Doc 0: "love love" -> love freq=2
        Doc 1: "love"      -> love freq=1
        """
        indexer = Indexer()
        indexer.add_document("love love")
        indexer.add_document("love")
        indexer.build_index()
        
        assert indexer.index["love"][0]["frequency"] == 2
        assert indexer.index["love"][1]["frequency"] == 1
    
    def test_indexer_get_index_entry_returns_stats(self):
        """
        Test get_index_entry returns full stats for a word.
        
        Should return dict of {doc_id: {frequency, positions}}.
        """
        indexer = Indexer()
        indexer.add_document("love work love")
        indexer.build_index()
        
        entry = indexer.get_index_entry("love")
        assert entry is not None
        assert 0 in entry
        assert entry[0]["frequency"] == 2
        assert entry[0]["positions"] == [0, 2]
    
    def test_indexer_get_index_entry_returns_none_for_unknown(self):
        """
        Test get_index_entry returns None for unknown word.
        """
        indexer = Indexer()
        indexer.add_document("hello world")
        indexer.build_index()
        
        assert indexer.get_index_entry("unicorn") is None
    
    def test_indexer_finds_documents_with_single_word(self):
        """
        Test that search finds documents containing a word.
        
        Should return list of document IDs for given word.
        """
        indexer = Indexer()
        indexer.add_document("The quick brown fox jumps over the lazy dog")
        indexer.add_document("A quick brown cat runs fast")
        indexer.build_index()
        
        results = indexer.search("quick")
        
        assert isinstance(results, list)
        assert 0 in results
        assert 1 in results
        assert len(results) == 2
    
    def test_indexer_returns_empty_for_unknown_word(self):
        """
        Test that search returns empty list for unknown word.
        
        Should gracefully handle words not in index.
        """
        indexer = Indexer()
        indexer.add_document("The quick brown fox")
        indexer.build_index()
        
        results = indexer.search("unicorn")
        
        assert results == []
    
    def test_indexer_handles_duplicate_words_in_document(self):
        """
        Test that duplicate words in same doc are deduplicated.
        
        Should not add same document multiple times for repeated words.
        """
        indexer = Indexer()
        indexer.add_document("love love love is love")
        indexer.build_index()
        
        results = indexer.search("love")
        
        # Document 0 should appear only once, not 4 times
        assert results == [0]
        assert results.count(0) == 1
    
    def test_indexer_handles_empty_document(self):
        """
        Test that Indexer handles empty documents gracefully.
        
        Should accept empty string without crashing.
        """
        indexer = Indexer()
        doc_id = indexer.add_document("")
        indexer.build_index()
        
        assert doc_id == 0
        # Empty doc should not create any index entries
        assert indexer.index == {}
    
    # ========== CASE SENSITIVITY TESTS ==========
    
    def test_indexer_is_case_insensitive(self):
        """
        Test that search is case-insensitive.
        
        Should find documents regardless of case.
        """
        indexer = Indexer()
        indexer.add_document("The QUICK brown FOX")
        indexer.build_index()
        
        # All these should find the document
        assert 0 in indexer.search("quick")
        assert 0 in indexer.search("QUICK")
        assert 0 in indexer.search("Quick")
        assert 0 in indexer.search("fox")
        assert 0 in indexer.search("FOX")
    
    # ========== PUNCTUATION HANDLING TESTS ==========
    
    def test_indexer_handles_punctuation(self):
        """
        Test that Indexer removes punctuation.
        
        Should tokenize "hello," -> "hello" not "hello,"
        """
        indexer = Indexer()
        indexer.add_document("Hello, world! How are you?")
        indexer.build_index()
        
        # Search for word without punctuation should find it
        assert 0 in indexer.search("hello")
        assert 0 in indexer.search("world")
        assert 0 in indexer.search("are")
    
    # ========== INTEGRATION TESTS ==========
    
    def test_indexer_complete_workflow(self):
        """
        Integration test: complete workflow from documents to search.
        
        Combines adding multiple documents, building index, and searching.
        """
        indexer = Indexer()
        
        # Add multiple documents
        indexer.add_document("The only way to do great work is to love what you do")
        indexer.add_document("Life is what happens while you're busy making other plans")
        indexer.add_document("The future belongs to those who believe in the beauty of their dreams")
        
        # Build index
        indexer.build_index()
        
        # Search for common words
        way_docs = indexer.search("way")
        life_docs = indexer.search("life")
        future_docs = indexer.search("future")
        
        # Verify results
        assert 0 in way_docs
        assert 1 in life_docs
        assert 2 in future_docs
        
        # Search for word appearing in multiple docs
        beauty_docs = indexer.search("beauty")  # only in doc 2
        assert beauty_docs == [2]
