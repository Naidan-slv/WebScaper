"""Tests for indexer.py.

Includes inverted index creation, word-frequency analysis, and JSON persistence.
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from src.indexer import Indexer, Persistence, WordFrequency

# ===== Inverted index tests =====

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


# ============================================================
# URL Storage Tests
# ============================================================

class TestIndexerUrls:
    """Tests for storing page URLs alongside documents."""

    def test_add_document_with_url(self):
        """add_document accepts optional url parameter and stores it."""
        indexer = Indexer()
        doc_id = indexer.add_document("hello world", url="http://example.com/page/1/")
        assert doc_id == 0
        assert indexer.get_document_url(doc_id) == "http://example.com/page/1/"

    def test_add_document_without_url(self):
        """add_document without url still works (backward compat)."""
        indexer = Indexer()
        doc_id = indexer.add_document("hello world")
        assert doc_id == 0
        assert indexer.get_document_url(doc_id) is None

    def test_get_document_url_multiple_docs(self):
        """Each document stores its own URL."""
        indexer = Indexer()
        indexer.add_document("page one", url="http://example.com/1/")
        indexer.add_document("page two", url="http://example.com/2/")
        assert indexer.get_document_url(0) == "http://example.com/1/"
        assert indexer.get_document_url(1) == "http://example.com/2/"

    def test_get_document_url_unknown_doc(self):
        """get_document_url returns None for unknown doc_id."""
        indexer = Indexer()
        assert indexer.get_document_url(99) is None

    def test_documents_dict_still_stores_text(self):
        """documents dict stays as {id: text} for backward compat."""
        indexer = Indexer()
        indexer.add_document("hello world", url="http://example.com/")
        assert indexer.documents[0] == "hello world"


# ===== Persistence tests =====

class TestPersistenceInit:
    """Tests for Persistence initialization."""

    def test_init_with_valid_indexer(self):
        """Persistence initializes with valid indexer."""
        indexer = Mock()
        persistence = Persistence(indexer)
        
        assert persistence.indexer == indexer

    def test_init_raises_error_if_indexer_none(self):
        """Persistence raises ValueError if indexer is None."""
        with pytest.raises(ValueError):
            Persistence(None)


class TestSaveIndex:
    """Tests for saving index to file."""

    @pytest.fixture
    def persistence_setup(self):
        """Provide persistence with mock indexer."""
        indexer = Mock()
        indexer.index = {"love": [1, 2], "search": [3]}
        indexer.documents = {1: "text1", 2: "text2", 3: "text3"}
        return Persistence(indexer)

    def test_save_index_creates_json_file(self, persistence_setup):
        """save_index creates JSON file with index data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = f"{tmpdir}/index.json"
            
            byte_count = persistence_setup.save_index(filepath)
            
            assert Path(filepath).exists()
            assert byte_count > 0
            
            with open(filepath) as f:
                data = json.load(f)
            assert "love" in data
            assert "search" in data

    def test_save_index_raises_error_if_filepath_none(self, persistence_setup):
        """save_index raises ValueError if filepath is None."""
        with pytest.raises(ValueError):
            persistence_setup.save_index(None)

    def test_save_index_raises_error_if_filepath_empty(self, persistence_setup):
        """save_index raises ValueError if filepath is empty."""
        with pytest.raises(ValueError):
            persistence_setup.save_index("")

    def test_save_index_raises_error_if_index_empty(self):
        """save_index raises ValueError if index is empty."""
        indexer = Mock()
        indexer.index = {}  # Empty index
        persistence = Persistence(indexer)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.raises(ValueError):
                persistence.save_index(f"{tmpdir}/index.json")

    def test_save_index_handles_file_permission_error(self, persistence_setup):
        """save_index propagates file permission errors."""
        with patch("builtins.open", side_effect=PermissionError("No permission")):
            with pytest.raises(OSError):
                persistence_setup.save_index("/protected/path/index.json")


class TestLoadIndex:
    """Tests for loading index from file."""

    @pytest.fixture
    def index_file(self):
        """Create a temporary index file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = f"{tmpdir}/index.json"
            data = {"love": [1, 2], "search": [3]}
            with open(filepath, "w") as f:
                json.dump(data, f)
            yield filepath

    def test_load_index_reads_json_file(self, index_file):
        """load_index reads and parses JSON file."""
        indexer = Mock()
        persistence = Persistence(indexer)
        
        data = persistence.load_index(index_file)
        
        assert data == {"love": [1, 2], "search": [3]}

    def test_load_index_raises_error_if_filepath_none(self):
        """load_index raises ValueError if filepath is None."""
        indexer = Mock()
        persistence = Persistence(indexer)
        
        with pytest.raises(ValueError):
            persistence.load_index(None)

    def test_load_index_raises_error_if_file_not_found(self):
        """load_index raises FileNotFoundError if file not found."""
        indexer = Mock()
        persistence = Persistence(indexer)
        
        with pytest.raises(FileNotFoundError):
            persistence.load_index("/nonexistent/path/index.json")

    def test_load_index_raises_error_if_json_invalid(self):
        """load_index raises JSONDecodeError if JSON malformed."""
        indexer = Mock()
        persistence = Persistence(indexer)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = f"{tmpdir}/bad.json"
            with open(filepath, "w") as f:
                f.write("{invalid json}")
            
            with pytest.raises(json.JSONDecodeError):
                persistence.load_index(filepath)


class TestSaveDocuments:
    """Tests for saving documents to file."""

    @pytest.fixture
    def persistence_setup(self):
        """Provide persistence with mock indexer."""
        indexer = Mock()
        indexer.index = {"word": [1]}
        indexer.documents = {1: "doc text 1", 2: "doc text 2"}
        return Persistence(indexer)

    def test_save_documents_creates_json_file(self, persistence_setup):
        """save_documents creates JSON file with documents."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = f"{tmpdir}/documents.json"
            
            byte_count = persistence_setup.save_documents(filepath)
            
            assert Path(filepath).exists()
            assert byte_count > 0
            
            with open(filepath) as f:
                data = json.load(f)
            # JSON converts int keys to strings
            assert "1" in data
            assert "2" in data

    def test_save_documents_raises_error_if_documents_empty(self):
        """save_documents raises ValueError if documents empty."""
        indexer = Mock()
        indexer.index = {"word": [1]}
        indexer.documents = {}  # Empty documents
        persistence = Persistence(indexer)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.raises(ValueError):
                persistence.save_documents(f"{tmpdir}/docs.json")

    def test_save_documents_raises_error_if_filepath_none(self, persistence_setup):
        """save_documents raises ValueError if filepath is None."""
        with pytest.raises(ValueError):
            persistence_setup.save_documents(None)


class TestLoadDocuments:
    """Tests for loading documents from file."""

    @pytest.fixture
    def documents_file(self):
        """Create a temporary documents file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = f"{tmpdir}/documents.json"
            data = {1: "doc text 1", 2: "doc text 2"}
            with open(filepath, "w") as f:
                json.dump(data, f)
            yield filepath

    def test_load_documents_reads_json_file(self, documents_file):
        """load_documents reads and parses JSON file."""
        indexer = Mock()
        persistence = Persistence(indexer)
        
        data = persistence.load_documents(documents_file)
        
        # JSON keys are strings, not integers
        assert data == {"1": "doc text 1", "2": "doc text 2"}

    def test_load_documents_raises_error_if_file_not_found(self):
        """load_documents raises FileNotFoundError if file not found."""
        indexer = Mock()
        persistence = Persistence(indexer)
        
        with pytest.raises(FileNotFoundError):
            persistence.load_documents("/nonexistent/path/documents.json")

    def test_load_documents_raises_error_if_json_invalid(self):
        """load_documents raises JSONDecodeError if JSON malformed."""
        indexer = Mock()
        persistence = Persistence(indexer)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = f"{tmpdir}/bad.json"
            with open(filepath, "w") as f:
                f.write("{bad json}")
            
            with pytest.raises(json.JSONDecodeError):
                persistence.load_documents(filepath)


class TestSaveCheckpoint:
    """Tests for checkpoint save (combined index + documents)."""

    @pytest.fixture
    def persistence_setup(self):
        """Provide persistence with mock indexer."""
        indexer = Mock()
        indexer.index = {"word": [1, 2]}
        indexer.documents = {1: "text1", 2: "text2"}
        return Persistence(indexer)

    def test_save_checkpoint_creates_directory_with_files(self, persistence_setup):
        """save_checkpoint creates directory with index + documents files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            checkpoint_dir = f"{tmpdir}/checkpoint"
            
            result = persistence_setup.save_checkpoint(checkpoint_dir)
            
            assert Path(checkpoint_dir).exists()
            assert "index_file" in result
            assert "docs_file" in result
            assert result["index_file"] > 0
            assert result["docs_file"] > 0

    def test_save_checkpoint_raises_error_if_dirpath_none(self, persistence_setup):
        """save_checkpoint raises ValueError if dirpath is None."""
        with pytest.raises(ValueError):
            persistence_setup.save_checkpoint(None)

    def test_save_checkpoint_files_are_valid_json(self, persistence_setup):
        """save_checkpoint creates valid JSON files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            checkpoint_dir = f"{tmpdir}/checkpoint"
            
            persistence_setup.save_checkpoint(checkpoint_dir)
            
            # Verify files are valid JSON
            index_file = Path(checkpoint_dir) / "index.json"
            docs_file = Path(checkpoint_dir) / "documents.json"
            
            with open(index_file) as f:
                json.load(f)  # Should not raise
            with open(docs_file) as f:
                json.load(f)  # Should not raise


class TestLoadCheckpoint:
    """Tests for checkpoint load (combined index + documents)."""

    @pytest.fixture
    def checkpoint_dir(self):
        """Create a temporary checkpoint directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            checkpoint_path = Path(tmpdir) / "checkpoint"
            checkpoint_path.mkdir()
            
            # Create index file
            with open(checkpoint_path / "index.json", "w") as f:
                json.dump({"word": [1, 2]}, f)
            
            # Create documents file
            with open(checkpoint_path / "documents.json", "w") as f:
                json.dump({1: "text1", 2: "text2"}, f)
            
            yield str(checkpoint_path)

    def test_load_checkpoint_loads_both_files(self, checkpoint_dir):
        """load_checkpoint loads index and documents."""
        indexer = Mock()
        persistence = Persistence(indexer)
        
        result = persistence.load_checkpoint(checkpoint_dir)
        
        assert "index" in result
        assert "documents" in result
        assert result["index"] == {"word": [1, 2]}
        # JSON converts int keys to strings
        assert result["documents"] == {"1": "text1", "2": "text2"}

    def test_load_checkpoint_raises_error_if_dirpath_none(self):
        """load_checkpoint raises ValueError if dirpath is None."""
        indexer = Mock()
        persistence = Persistence(indexer)
        
        with pytest.raises(ValueError):
            persistence.load_checkpoint(None)

    def test_load_checkpoint_raises_error_if_directory_not_found(self):
        """load_checkpoint raises FileNotFoundError if directory not found."""
        indexer = Mock()
        persistence = Persistence(indexer)
        
        with pytest.raises(FileNotFoundError):
            persistence.load_checkpoint("/nonexistent/checkpoint")

    def test_load_checkpoint_raises_error_if_files_missing(self):
        """load_checkpoint raises FileNotFoundError if checkpoint files missing."""
        indexer = Mock()
        persistence = Persistence(indexer)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            checkpoint_dir = Path(tmpdir) / "checkpoint"
            checkpoint_dir.mkdir()
            # Create empty checkpoint directory (no files)
            
            with pytest.raises(FileNotFoundError):
                persistence.load_checkpoint(str(checkpoint_dir))


class TestPersistenceIntegration:
    """Integration tests for full save/load workflow."""

    def test_full_save_and_load_workflow(self):
        """Full workflow: save index + docs, then load them back."""
        indexer = Mock()
        indexer.index = {"love": [1, 2, 3], "life": [2]}
        indexer.documents = {1: "Love is important", 2: "Love life all day", 3: "Life happens"}
        
        persistence = Persistence(indexer)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            checkpoint_dir = f"{tmpdir}/checkpoint"
            
            # Save
            save_result = persistence.save_checkpoint(checkpoint_dir)
            assert save_result["index_file"] > 0
            assert save_result["docs_file"] > 0
            
            # Load
            load_result = persistence.load_checkpoint(checkpoint_dir)
            
            # Verify data integrity
            assert load_result["index"] == indexer.index
            # JSON converts int keys to strings; documents now saved as {"text": str}
            assert load_result["documents"] == {
                "1": {"text": "Love is important"},
                "2": {"text": "Love life all day"},
                "3": {"text": "Life happens"}
            }

    def test_save_and_load_preserves_data_types(self):
        """Save/load preserves data types (int keys -> string keys in JSON)."""
        indexer = Mock()
        indexer.index = {"word": [1, 2, 3]}
        indexer.documents = {1: "text1", 2: "text2"}
        
        persistence = Persistence(indexer)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            checkpoint_dir = f"{tmpdir}/checkpoint"
            persistence.save_checkpoint(checkpoint_dir)
            result = persistence.load_checkpoint(checkpoint_dir)
            
            # Note: JSON converts integer keys to strings
            # This is expected behavior to verify
            assert "word" in result["index"]
            assert isinstance(result["index"]["word"], list)
            # Documents keys are strings after JSON round-trip
            assert "1" in result["documents"]
            assert "2" in result["documents"]


# ===== Word-frequency tests =====

class TestWordFrequencyInit:
    """Tests for WordFrequency initialization."""

    @pytest.fixture
    def mock_indexer(self):
        """Provide mock Indexer with documents."""
        indexer = Mock()
        indexer.documents = {
            0: "the cat and the dog",
            1: "the quick brown fox"
        }
        indexer.index = {
            "the": [0, 1],
            "cat": [0],
            "and": [0],
            "dog": [0],
            "quick": [1],
            "brown": [1],
            "fox": [1]
        }
        return indexer

    def test_init_with_valid_indexer(self, mock_indexer):
        """WordFrequency initializes with valid Indexer."""
        wf = WordFrequency(mock_indexer)
        
        assert wf.indexer == mock_indexer

    def test_init_raises_error_if_indexer_none(self):
        """WordFrequency raises ValueError if indexer is None."""
        with pytest.raises(ValueError):
            WordFrequency(None)

    def test_init_raises_error_if_indexer_empty(self):
        """WordFrequency raises ValueError if indexer has no documents."""
        indexer = Mock()
        indexer.documents = {}
        indexer.index = {}
        
        with pytest.raises(ValueError):
            WordFrequency(indexer)

    def test_init_raises_error_if_no_index(self):
        """WordFrequency raises ValueError if index not built."""
        indexer = Mock()
        indexer.documents = {0: "some text"}
        indexer.index = {}
        
        with pytest.raises(ValueError):
            WordFrequency(indexer)


class TestCalculateFrequencies:
    """Tests for frequency calculation."""

    @pytest.fixture
    def wf_setup(self):
        """Provide WordFrequency with mock indexer."""
        indexer = Mock()
        indexer.documents = {
            0: "the cat and the dog the",
            1: "the quick brown fox",
            2: "fox and fox"
        }
        indexer.index = {
            "the": [0, 1],
            "cat": [0],
            "and": [0, 2],
            "dog": [0],
            "quick": [1],
            "brown": [1],
            "fox": [1, 2]
        }
        return WordFrequency(indexer)

    def test_calculate_frequencies_returns_dict(self, wf_setup):
        """calculate_frequencies returns dict structure."""
        freqs = wf_setup.calculate_frequencies()
        
        assert isinstance(freqs, dict)
        assert all(isinstance(k, int) for k in freqs.keys())
        assert all(isinstance(v, dict) for v in freqs.values())

    def test_calculate_frequencies_counts_correctly(self, wf_setup):
        """calculate_frequencies counts word occurrences correctly."""
        freqs = wf_setup.calculate_frequencies()
        
        # Document 0: "the cat and the dog the" = 5 "the", 1 "cat", 1 "and", 1 "dog"
        assert freqs[0]["the"] == 3
        assert freqs[0]["cat"] == 1
        assert freqs[0]["and"] == 1
        assert freqs[0]["dog"] == 1

    def test_calculate_frequencies_multiple_docs(self, wf_setup):
        """calculate_frequencies processes all documents."""
        freqs = wf_setup.calculate_frequencies()
        
        assert len(freqs) == 3
        assert 0 in freqs
        assert 1 in freqs
        assert 2 in freqs

    def test_calculate_frequencies_doc_2(self, wf_setup):
        """calculate_frequencies handles different word patterns."""
        freqs = wf_setup.calculate_frequencies()
        
        # Document 2: "fox and fox" = 2 "fox", 1 "and"
        assert freqs[2]["fox"] == 2
        assert freqs[2]["and"] == 1


class TestGetWordFrequency:
    """Tests for single word frequency lookup."""

    @pytest.fixture
    def wf_setup(self):
        """Provide WordFrequency with calculated frequencies."""
        indexer = Mock()
        indexer.documents = {
            0: "the cat and the dog the",
            1: "the fox"
        }
        indexer.index = {
            "the": [0, 1],
            "cat": [0],
            "and": [0],
            "dog": [0],
            "fox": [1]
        }
        wf = WordFrequency(indexer)
        wf.frequencies = wf.calculate_frequencies()
        return wf

    def test_get_word_frequency_returns_count(self, wf_setup):
        """get_word_frequency returns frequency for given word."""
        freq = wf_setup.get_word_frequency("the", 0)
        
        assert freq == 3

    def test_get_word_frequency_single_occurrence(self, wf_setup):
        """get_word_frequency returns 1 for single occurrence."""
        freq = wf_setup.get_word_frequency("cat", 0)
        
        assert freq == 1

    def test_get_word_frequency_case_insensitive(self, wf_setup):
        """get_word_frequency is case-insensitive."""
        freq1 = wf_setup.get_word_frequency("the", 0)
        freq2 = wf_setup.get_word_frequency("THE", 0)
        
        assert freq1 == freq2 == 3

    def test_get_word_frequency_word_not_in_doc(self, wf_setup):
        """get_word_frequency returns 0 for word not in document."""
        freq = wf_setup.get_word_frequency("fox", 0)
        
        assert freq == 0

    def test_get_word_frequency_raises_error_invalid_doc(self, wf_setup):
        """get_word_frequency raises KeyError for invalid doc_id."""
        with pytest.raises(KeyError):
            wf_setup.get_word_frequency("the", 999)

    def test_get_word_frequency_raises_error_invalid_word(self, wf_setup):
        """get_word_frequency raises ValueError for None word."""
        with pytest.raises(ValueError):
            wf_setup.get_word_frequency(None, 0)


class TestGetTopWords:
    """Tests for getting top frequent words."""

    @pytest.fixture
    def wf_setup(self):
        """Provide WordFrequency with calculated frequencies."""
        indexer = Mock()
        indexer.documents = {
            0: "the the the cat cat dog and and fox fox fox fox",
        }
        indexer.index = {
            "the": [0],
            "cat": [0],
            "dog": [0],
            "and": [0],
            "fox": [0]
        }
        wf = WordFrequency(indexer)
        wf.frequencies = wf.calculate_frequencies()
        return wf

    def test_get_top_words_returns_list(self, wf_setup):
        """get_top_words returns list of dicts."""
        top = wf_setup.get_top_words(0)
        
        assert isinstance(top, list)
        assert all(isinstance(item, dict) for item in top)

    def test_get_top_words_sorted_by_frequency(self, wf_setup):
        """get_top_words returns words sorted by frequency (descending)."""
        top = wf_setup.get_top_words(0)
        
        freqs = [item["frequency"] for item in top]
        assert freqs == sorted(freqs, reverse=True)

    def test_get_top_words_contains_word_and_frequency(self, wf_setup):
        """get_top_words includes 'word' and 'frequency' keys."""
        top = wf_setup.get_top_words(0)
        
        assert all("word" in item and "frequency" in item for item in top)

    def test_get_top_words_limit(self, wf_setup):
        """get_top_words respects limit parameter."""
        top3 = wf_setup.get_top_words(0, limit=3)
        top1 = wf_setup.get_top_words(0, limit=1)
        
        assert len(top3) == 3
        assert len(top1) == 1

    def test_get_top_words_most_frequent_first(self, wf_setup):
        """get_top_words returns most frequent word first."""
        top = wf_setup.get_top_words(0, limit=1)
        
        # "fox" appears 4 times (most frequent)
        assert top[0]["word"] == "fox"
        assert top[0]["frequency"] == 4

    def test_get_top_words_raises_error_invalid_doc(self, wf_setup):
        """get_top_words raises KeyError for invalid doc_id."""
        with pytest.raises(KeyError):
            wf_setup.get_top_words(999)


class TestGetDocumentLength:
    """Tests for document length (word count)."""

    @pytest.fixture
    def wf_setup(self):
        """Provide WordFrequency with calculated frequencies."""
        indexer = Mock()
        indexer.documents = {
            0: "the cat and dog",  # 4 words
            1: "hello world",      # 2 words
            2: "a b c d e f g"     # 7 words
        }
        indexer.index = {
            "the": [0],
            "cat": [0],
            "and": [0],
            "dog": [0],
            "hello": [1],
            "world": [1],
            "a": [2],
            "b": [2],
            "c": [2],
            "d": [2],
            "e": [2],
            "f": [2],
            "g": [2]
        }
        wf = WordFrequency(indexer)
        wf.frequencies = wf.calculate_frequencies()
        return wf

    def test_get_document_length_returns_int(self, wf_setup):
        """get_document_length returns integer word count."""
        length = wf_setup.get_document_length(0)
        
        assert isinstance(length, int)

    def test_get_document_length_correct_count(self, wf_setup):
        """get_document_length counts words correctly."""
        len0 = wf_setup.get_document_length(0)
        len1 = wf_setup.get_document_length(1)
        len2 = wf_setup.get_document_length(2)
        
        assert len0 == 4
        assert len1 == 2
        assert len2 == 7

    def test_get_document_length_raises_error_invalid_doc(self, wf_setup):
        """get_document_length raises KeyError for invalid doc_id."""
        with pytest.raises(KeyError):
            wf_setup.get_document_length(999)


class TestWordFrequencyIntegration:
    """Integration tests for WordFrequency workflow."""

    def test_full_word_frequency_workflow(self):
        """Full workflow: init → calculate → lookup → top words."""
        indexer = Mock()
        indexer.documents = {
            0: "apple apple banana cherry banana apple",
            1: "date elderberry fig grape"
        }
        indexer.index = {
            "apple": [0],
            "banana": [0],
            "cherry": [0],
            "date": [1],
            "elderberry": [1],
            "fig": [1],
            "grape": [1]
        }
        
        wf = WordFrequency(indexer)
        
        # Calculate frequencies
        freqs = wf.calculate_frequencies()
        assert len(freqs) == 2
        
        # Get specific word frequency
        apple_freq = wf.get_word_frequency("apple", 0)
        assert apple_freq == 3
        
        # Get top words
        top = wf.get_top_words(0, limit=2)
        assert top[0]["word"] == "apple"
        assert top[0]["frequency"] == 3
        
        # Get document length
        length = wf.get_document_length(0)
        assert length == 6
