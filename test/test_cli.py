"""
Comprehensive tests for CLI class.

Tests cover:
- Initialization with validation
- Index building from website
- Query execution with results
- Result formatting
- Interactive REPL workflow
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, call
from src.cli import CLI


class TestCLIInit:
    """Tests for CLI initialization and validation."""

    def test_init_with_valid_components(self):
        """CLI initializes successfully with valid crawler, indexer, search."""
        crawler = Mock()
        indexer = Mock()
        indexer.index = {"word": [1, 2, 3]}  # Built index
        search = Mock()
        
        cli = CLI(crawler, indexer, search)
        
        assert cli.crawler == crawler
        assert cli.indexer == indexer
        assert cli.search == search

    def test_init_raises_error_if_crawler_none(self):
        """CLI raises ValueError if crawler is None."""
        indexer = Mock()
        indexer.index = {"word": [1]}
        search = Mock()
        
        with pytest.raises(ValueError):
            CLI(None, indexer, search)

    def test_init_raises_error_if_indexer_none(self):
        """CLI raises ValueError if indexer is None."""
        crawler = Mock()
        search = Mock()
        
        with pytest.raises(ValueError):
            CLI(crawler, None, search)

    def test_init_raises_error_if_search_none(self):
        """CLI raises ValueError if search is None."""
        crawler = Mock()
        indexer = Mock()
        indexer.index = {"word": [1]}
        
        with pytest.raises(ValueError):
            CLI(crawler, indexer, None)

    def test_init_raises_error_if_indexer_not_built(self):
        """CLI raises RuntimeError if indexer.index is empty (not built)."""
        crawler = Mock()
        indexer = Mock()
        indexer.index = {}  # Empty - not built
        search = Mock()
        
        with pytest.raises(RuntimeError):
            CLI(crawler, indexer, search)

    def test_init_raises_error_if_indexer_missing_index_attribute(self):
        """CLI raises RuntimeError if indexer lacks index attribute."""
        crawler = Mock()
        indexer = Mock(spec=[])  # No index attribute
        search = Mock()
        
        with pytest.raises(RuntimeError):
            CLI(crawler, indexer, search)


class TestBuildIndex:
    """Tests for index building from website."""

    @pytest.fixture
    def cli_setup(self):
        """Provide mock components for CLI."""
        crawler = Mock()
        indexer = Mock()
        indexer.index = {"word": [1]}  # Pre-built for init
        search = Mock()
        return CLI(crawler, indexer, search)

    def test_build_index_fetches_page_and_builds_index(self, cli_setup):
        """build_index fetches URL and builds search index."""
        cli_setup.crawler.fetch_page.return_value = (
            "<html><body>Hello world</body></html>"
        )
        cli_setup.indexer.add_document.return_value = None
        cli_setup.indexer.build_index.return_value = None
        cli_setup.indexer.documents = {1: "doc1"}
        
        doc_count = cli_setup.build_index("https://example.com")
        
        cli_setup.crawler.fetch_page.assert_called_once_with("https://example.com")
        cli_setup.indexer.add_document.assert_called_once()
        cli_setup.indexer.build_index.assert_called_once()
        assert doc_count >= 1

    def test_build_index_raises_error_if_url_invalid(self, cli_setup):
        """build_index raises ValueError if URL is invalid."""
        with pytest.raises(ValueError):
            cli_setup.build_index(None)

    def test_build_index_raises_error_if_crawler_fails(self, cli_setup):
        """build_index raises exception if crawler fails."""
        cli_setup.crawler.fetch_page.side_effect = Exception("Network error")
        
        with pytest.raises(Exception):
            cli_setup.build_index("https://example.com")

    def test_build_index_raises_error_if_indexer_fails(self, cli_setup):
        """build_index raises exception if indexer fails to build."""
        cli_setup.crawler.fetch_page.return_value = "<html>test</html>"
        cli_setup.indexer.build_index.side_effect = Exception("Index error")
        
        with pytest.raises(Exception):
            cli_setup.build_index("https://example.com")

    def test_build_index_returns_document_count(self, cli_setup):
        """build_index returns number of documents indexed."""
        cli_setup.crawler.fetch_page.return_value = "<html>test</html>"
        cli_setup.indexer.add_document.return_value = None
        cli_setup.indexer.build_index.return_value = None
        cli_setup.indexer.documents = {1: "doc1", 2: "doc2", 3: "doc3"}
        
        doc_count = cli_setup.build_index("https://example.com")
        
        assert doc_count == 3


class TestSearchQuery:
    """Tests for search query execution."""

    @pytest.fixture
    def cli_setup(self):
        """Provide mock components for CLI."""
        crawler = Mock()
        indexer = Mock()
        indexer.index = {"word": [1]}
        search = Mock()
        return CLI(crawler, indexer, search)

    def test_search_query_executes_search_and_returns_results(self, cli_setup):
        """search_query executes search and returns formatted results."""
        cli_setup.search.search_with_snippets.return_value = [
            {"doc_id": 1, "snippet": "Hello world", "text": "Full text here"}
        ]
        
        results = cli_setup.search_query("hello")
        
        cli_setup.search.search_with_snippets.assert_called_once_with("hello")
        assert len(results) == 1
        assert results[0]["doc_id"] == 1

    def test_search_query_returns_empty_list_if_no_results(self, cli_setup):
        """search_query returns empty list if search finds nothing."""
        cli_setup.search.search_with_snippets.return_value = []
        
        results = cli_setup.search_query("nonexistent")
        
        assert results == []

    def test_search_query_raises_error_if_query_none(self, cli_setup):
        """search_query raises ValueError if query is None."""
        with pytest.raises(ValueError):
            cli_setup.search_query(None)

    def test_search_query_raises_error_if_query_empty(self, cli_setup):
        """search_query raises ValueError if query is empty string."""
        with pytest.raises(ValueError):
            cli_setup.search_query("")

    def test_search_query_handles_search_exceptions(self, cli_setup):
        """search_query propagates exceptions from search component."""
        cli_setup.search.search_with_snippets.side_effect = RuntimeError("Search failed")
        
        with pytest.raises(RuntimeError):
            cli_setup.search_query("test")

    def test_search_query_normalizes_query_input(self, cli_setup):
        """search_query normalizes query before searching."""
        cli_setup.search.search_with_snippets.return_value = []
        
        cli_setup.search_query("HELLO WORLD")
        
        # Should lowercase the query
        cli_setup.search.search_with_snippets.assert_called_once()
        call_args = cli_setup.search.search_with_snippets.call_args[0][0]
        assert call_args == call_args.lower()


class TestDisplayResults:
    """Tests for result formatting and display."""

    @pytest.fixture
    def cli_setup(self):
        """Provide mock components for CLI."""
        crawler = Mock()
        indexer = Mock()
        indexer.index = {"word": [1]}
        search = Mock()
        return CLI(crawler, indexer, search)

    def test_display_results_formats_single_result(self, cli_setup):
        """display_results formats single search result."""
        results = [{"doc_id": 1, "snippet": "Hello world", "text": "Full text"}]
        
        output = cli_setup.display_results("hello", results)
        
        assert "hello" in output.lower()
        assert "1" in output
        assert "Hello world" in output

    def test_display_results_formats_multiple_results(self, cli_setup):
        """display_results formats multiple search results."""
        results = [
            {"doc_id": 1, "snippet": "First result", "text": "Text 1"},
            {"doc_id": 2, "snippet": "Second result", "text": "Text 2"},
        ]
        
        output = cli_setup.display_results("query", results)
        
        assert "First result" in output
        assert "Second result" in output

    def test_display_results_handles_no_results(self, cli_setup):
        """display_results handles empty result list gracefully."""
        output = cli_setup.display_results("notfound", [])
        
        assert isinstance(output, str)
        assert len(output) > 0

    def test_display_results_includes_doc_id(self, cli_setup):
        """display_results includes document ID in output."""
        results = [{"doc_id": 42, "snippet": "test", "text": "full"}]
        
        output = cli_setup.display_results("test", results)
        
        assert "42" in output

    def test_display_results_includes_snippet(self, cli_setup):
        """display_results includes snippet text in output."""
        results = [{"doc_id": 1, "snippet": "Custom snippet text", "text": "full"}]
        
        output = cli_setup.display_results("test", results)
        
        assert "Custom snippet text" in output


class TestRun:
    """Tests for interactive REPL workflow."""

    @pytest.fixture
    def cli_setup(self):
        """Provide mock components for CLI."""
        crawler = Mock()
        indexer = Mock()
        indexer.index = {"word": [1]}
        search = Mock()
        return CLI(crawler, indexer, search)

    @patch("builtins.input")
    def test_run_prompts_for_url_then_builds_index(self, mock_input, cli_setup):
        """run prompts for URL, builds index, enters search loop."""
        mock_input.side_effect = ["https://example.com", "quit"]
        cli_setup.crawler.fetch_page.return_value = "<html>test</html>"
        cli_setup.indexer.add_document.return_value = None
        cli_setup.indexer.build_index.return_value = None
        cli_setup.indexer.documents = {1: "doc"}
        
        cli_setup.run()
        
        cli_setup.crawler.fetch_page.assert_called_once()
        assert mock_input.call_count >= 1

    @patch("builtins.input")
    def test_run_accepts_search_queries(self, mock_input, cli_setup):
        """run accepts and executes search queries from user."""
        mock_input.side_effect = [
            "https://example.com",
            "hello",
            "quit",
        ]
        cli_setup.crawler.fetch_page.return_value = "<html>test</html>"
        cli_setup.indexer.build_index.return_value = None
        cli_setup.indexer.documents = {1: "doc"}
        cli_setup.search.search_with_snippets.return_value = [
            {"doc_id": 1, "snippet": "hello world", "text": "full"}
        ]
        
        cli_setup.run()
        
        cli_setup.search.search_with_snippets.assert_called()

    @patch("builtins.input")
    def test_run_exits_on_quit_command(self, mock_input, cli_setup):
        """run exits when user enters 'quit'."""
        mock_input.side_effect = ["https://example.com", "quit"]
        cli_setup.crawler.fetch_page.return_value = "<html>test</html>"
        cli_setup.indexer.build_index.return_value = None
        cli_setup.indexer.documents = {1: "doc"}
        
        # Should not raise exception
        cli_setup.run()

    @patch("builtins.input", side_effect=EOFError)
    def test_run_exits_on_eof(self, mock_input, cli_setup):
        """run exits gracefully on EOF (Ctrl+D)."""
        cli_setup.crawler.fetch_page.return_value = "<html>test</html>"
        cli_setup.indexer.build_index.return_value = None
        cli_setup.indexer.documents = {1: "doc"}
        mock_input.side_effect = ["https://example.com", EOFError()]
        
        cli_setup.run()

    @patch("builtins.input")
    @patch("builtins.print")
    def test_run_displays_search_results(self, mock_print, mock_input, cli_setup):
        """run displays search results to user."""
        mock_input.side_effect = [
            "https://example.com",
            "search term",
            "quit",
        ]
        cli_setup.crawler.fetch_page.return_value = "<html>test</html>"
        cli_setup.indexer.build_index.return_value = None
        cli_setup.indexer.documents = {1: "doc"}
        cli_setup.search.search_with_snippets.return_value = [
            {"doc_id": 1, "snippet": "result", "text": "full"}
        ]
        
        cli_setup.run()
        
        # Should have printed results
        assert mock_print.called

    @patch("builtins.input")
    def test_run_handles_empty_queries(self, mock_input, cli_setup):
        """run handles empty query strings gracefully."""
        mock_input.side_effect = [
            "https://example.com",
            "",  # Empty query
            "quit",
        ]
        cli_setup.crawler.fetch_page.return_value = "<html>test</html>"
        cli_setup.indexer.build_index.return_value = None
        cli_setup.indexer.documents = {1: "doc"}
        
        # Should not raise exception
        cli_setup.run()


class TestCLIIntegration:
    """Integration tests for full CLI workflow."""

    @patch("builtins.input")
    def test_full_workflow_build_and_search(self, mock_input):
        """Full workflow: initialize → build index → search → display."""
        crawler = Mock()
        indexer = Mock()
        indexer.index = {"word": [1]}
        indexer.documents = {1: "test document"}
        search = Mock()
        
        cli = CLI(crawler, indexer, search)
        
        mock_input.side_effect = [
            "https://example.com",
            "search",
            "quit",
        ]
        crawler.fetch_page.return_value = "<html>test document</html>"
        indexer.build_index.return_value = None
        search.search_with_snippets.return_value = [
            {"doc_id": 1, "snippet": "test", "text": "test document"}
        ]
        
        # Should execute without errors
        cli.run()
        
        crawler.fetch_page.assert_called_once()
        indexer.build_index.assert_called_once()
        search.search_with_snippets.assert_called_once()
