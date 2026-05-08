"""
Comprehensive tests for WordFrequency class.

Tests cover:
- Initialization with built indexer
- Frequency calculation for all documents
- Single word frequency lookup
- Top words by frequency
- Document length calculation
- Error handling (invalid inputs)
"""

import pytest
from unittest.mock import Mock
from src.indexer import WordFrequency


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
