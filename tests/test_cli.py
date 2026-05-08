"""
Tests for CLI class - matching COMP3011 coursework brief commands.

Tests cover the 4 required commands:
  > build   - Crawl website, build index, save to file
  > load    - Load previously saved index from file
  > print   - Print inverted index for a word
  > find    - Find pages containing search terms

Plus: initialization, REPL loop, help, error handling.
"""

import os
import json
import pytest
from unittest.mock import Mock, MagicMock, patch, PropertyMock
from src.main import CLI


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
