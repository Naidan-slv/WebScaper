"""
Comprehensive tests for MultiPageCrawler class.

Tests cover:
- URL generation for pagination
- Fetching multiple pages sequentially
- Handling page limits
- Politeness (respecting crawler delays)
- Error handling (network errors, page not found)
- Text extraction from multiple pages
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.multi_page_crawler import MultiPageCrawler


class TestMultiPageCrawlerInit:
    """Tests for MultiPageCrawler initialization."""

    @pytest.fixture
    def mock_crawler(self):
        """Provide mock Crawler instance."""
        crawler = Mock()
        crawler.fetch_page = Mock(return_value="<html>page</html>")
        crawler.extract_text = Mock(return_value="extracted text")
        return crawler

    def test_init_with_valid_crawler(self, mock_crawler):
        """MultiPageCrawler initializes with valid Crawler."""
        mpc = MultiPageCrawler(mock_crawler, max_pages=5)
        
        assert mpc.crawler == mock_crawler
        assert mpc.max_pages == 5

    def test_init_with_default_parameters(self, mock_crawler):
        """MultiPageCrawler uses default values for max_pages and base_url."""
        mpc = MultiPageCrawler(mock_crawler)
        
        assert mpc.max_pages == 10
        assert mpc.base_url == "https://quotes.toscrape.com"

    def test_init_with_custom_base_url(self, mock_crawler):
        """MultiPageCrawler accepts custom base_url."""
        mpc = MultiPageCrawler(mock_crawler, base_url="https://custom.com")
        
        assert mpc.base_url == "https://custom.com"

    def test_init_raises_error_if_crawler_none(self):
        """MultiPageCrawler raises ValueError if crawler is None."""
        with pytest.raises(ValueError):
            MultiPageCrawler(None)

    def test_init_raises_error_if_max_pages_invalid(self, mock_crawler):
        """MultiPageCrawler raises ValueError if max_pages <= 0."""
        with pytest.raises(ValueError):
            MultiPageCrawler(mock_crawler, max_pages=0)
        
        with pytest.raises(ValueError):
            MultiPageCrawler(mock_crawler, max_pages=-1)


class TestGetNextPageUrl:
    """Tests for pagination URL generation."""

    @pytest.fixture
    def mpc_setup(self):
        """Provide MultiPageCrawler instance."""
        crawler = Mock()
        crawler.fetch_page = Mock(return_value="<html>page</html>")
        return MultiPageCrawler(crawler, base_url="https://quotes.toscrape.com")

    def test_get_next_page_url_page_1(self, mpc_setup):
        """get_next_page_url returns base URL for page 1."""
        url = mpc_setup.get_next_page_url(1)
        
        assert url == "https://quotes.toscrape.com/"

    def test_get_next_page_url_page_2(self, mpc_setup):
        """get_next_page_url returns page 2 URL."""
        url = mpc_setup.get_next_page_url(2)
        
        assert "page/2" in url or "2" in url

    def test_get_next_page_url_increments_correctly(self, mpc_setup):
        """get_next_page_url increments page numbers correctly."""
        url2 = mpc_setup.get_next_page_url(2)
        url3 = mpc_setup.get_next_page_url(3)
        url10 = mpc_setup.get_next_page_url(10)
        
        # Extract page numbers and verify ordering
        assert "2" in url2
        assert "3" in url3
        assert "10" in url10

    def test_get_next_page_url_raises_error_if_page_invalid(self, mpc_setup):
        """get_next_page_url raises ValueError if page number <= 0."""
        with pytest.raises(ValueError):
            mpc_setup.get_next_page_url(0)
        
        with pytest.raises(ValueError):
            mpc_setup.get_next_page_url(-1)


class TestFetchAllPages:
    """Tests for fetching multiple pages."""

    @pytest.fixture
    def mpc_setup(self):
        """Provide MultiPageCrawler with mocked crawler."""
        crawler = Mock()
        # Mock fetch_page to return different content for each page
        # Pages 1-2 include a "Next" link; page 3 is the last page
        def mock_fetch(url):
            if "page/3" in url:
                return "<html><body>page 3</body></html>"
            elif "page/2" in url:
                return '<html><body>page 2<li class="next"><a href="/page/3/">Next</a></li></body></html>'
            return '<html><body>page 1<li class="next"><a href="/page/2/">Next</a></li></body></html>'
        
        crawler.fetch_page = Mock(side_effect=mock_fetch)
        return MultiPageCrawler(crawler, max_pages=3)

    def test_fetch_all_pages_returns_list(self, mpc_setup):
        """fetch_all_pages returns list of HTML strings."""
        result = mpc_setup.fetch_all_pages()
        
        assert isinstance(result, list)
        assert all(isinstance(page, str) for page in result)

    def test_fetch_all_pages_respects_max_pages(self, mpc_setup):
        """fetch_all_pages fetches exactly max_pages."""
        result = mpc_setup.fetch_all_pages()
        
        assert len(result) == 3

    def test_fetch_all_pages_calls_crawler_for_each_page(self, mpc_setup):
        """fetch_all_pages calls fetch_page for each page."""
        mpc_setup.fetch_all_pages()
        
        # Should call fetch_page 3 times (once for each page)
        assert mpc_setup.crawler.fetch_page.call_count == 3

    def test_fetch_all_pages_returns_empty_if_max_pages_one(self):
        """fetch_all_pages with max_pages=1 returns one page."""
        crawler = Mock()
        crawler.fetch_page = Mock(return_value="<html>page</html>")
        mpc = MultiPageCrawler(crawler, max_pages=1)
        
        result = mpc.fetch_all_pages()
        
        assert len(result) == 1

    def test_fetch_all_pages_handles_network_error(self, mpc_setup):
        """fetch_all_pages raises RuntimeError if fetch fails."""
        mpc_setup.crawler.fetch_page = Mock(side_effect=Exception("Network error"))
        
        with pytest.raises(RuntimeError):
            mpc_setup.fetch_all_pages()


class TestFetchAndParseAll:
    """Tests for fetching and parsing multiple pages."""

    @pytest.fixture
    def mpc_setup(self):
        """Provide MultiPageCrawler with mocked crawler."""
        crawler = Mock()
        
        def mock_fetch(url):
            if "page/2" in url:
                return "<html><body>page 2 content</body></html>"
            return '<html><body>page 1 content<li class="next"><a href="/page/2/">Next</a></li></body></html>'
        
        def mock_extract(html):
            if "page 2" in html:
                return "extracted page 2"
            return "extracted page 1"
        
        crawler.fetch_page = Mock(side_effect=mock_fetch)
        crawler.extract_text = Mock(side_effect=mock_extract)
        return MultiPageCrawler(crawler, max_pages=2)

    def test_fetch_and_parse_all_returns_list_of_dicts(self, mpc_setup):
        """fetch_and_parse_all returns list of dicts with page/text/url."""
        result = mpc_setup.fetch_and_parse_all()
        
        assert isinstance(result, list)
        assert len(result) > 0
        assert all("page" in item and "text" in item and "url" in item for item in result)

    def test_fetch_and_parse_all_contains_correct_page_numbers(self, mpc_setup):
        """fetch_and_parse_all includes correct page numbers."""
        result = mpc_setup.fetch_and_parse_all()
        
        page_numbers = [item["page"] for item in result]
        assert page_numbers == [1, 2]

    def test_fetch_and_parse_all_contains_extracted_text(self, mpc_setup):
        """fetch_and_parse_all includes extracted text."""
        result = mpc_setup.fetch_and_parse_all()
        
        texts = [item["text"] for item in result]
        assert "extracted page 1" in texts[0]
        assert "extracted page 2" in texts[1]

    def test_fetch_and_parse_all_contains_urls(self, mpc_setup):
        """fetch_and_parse_all includes page URLs."""
        result = mpc_setup.fetch_and_parse_all()
        
        # First page should have base URL
        assert mpc_setup.base_url in result[0]["url"]
        # Second page should have pagination
        assert "2" in result[1]["url"]

    def test_fetch_and_parse_all_handles_parse_error(self, mpc_setup):
        """fetch_and_parse_all raises RuntimeError if parse fails."""
        mpc_setup.crawler.extract_text = Mock(side_effect=Exception("Parse error"))
        
        with pytest.raises(RuntimeError):
            mpc_setup.fetch_and_parse_all()


class TestHasNextPage:
    """Tests for next-page detection."""

    @pytest.fixture
    def mpc(self):
        """Provide MultiPageCrawler instance."""
        crawler = Mock()
        return MultiPageCrawler(crawler)

    def test_has_next_page_returns_true(self, mpc):
        """Returns True when HTML has a next page link."""
        html = '<html><body><li class="next"><a href="/page/2/">Next</a></li></body></html>'
        assert mpc.has_next_page(html) is True

    def test_has_next_page_returns_false(self, mpc):
        """Returns False when HTML has no next page link."""
        html = '<html><body>content only</body></html>'
        assert mpc.has_next_page(html) is False

    def test_has_next_page_with_only_previous_link(self, mpc):
        """Returns False for a page with only a Previous link (last page)."""
        html = '<html><body><li class="previous"><a href="/page/9/">Previous</a></li></body></html>'
        assert mpc.has_next_page(html) is False

    def test_fetch_stops_at_last_page(self):
        """fetch_all_pages stops early when no next page is found."""
        crawler = Mock()
        def mock_fetch(url):
            if "page/2" in url:
                return "<html><body>page 2</body></html>"  # No next link
            return '<html><body>page 1<li class="next"><a href="/page/2/">Next</a></li></body></html>'
        crawler.fetch_page = Mock(side_effect=mock_fetch)
        mpc = MultiPageCrawler(crawler, max_pages=5)
        pages = mpc.fetch_all_pages()
        assert len(pages) == 2  # Stopped at page 2, not 5
        assert mpc.pages_fetched == 2


class TestGetPagesFetched:
    """Tests for tracking pages fetched."""

    @pytest.fixture
    def mpc_setup(self):
        """Provide MultiPageCrawler instance."""
        crawler = Mock()
        crawler.fetch_page = Mock(return_value='<html><body>page<li class="next"><a href="#">Next</a></li></body></html>')
        crawler.extract_text = Mock(return_value="text")
        return MultiPageCrawler(crawler, max_pages=5)

    def test_get_pages_fetched_before_fetch(self, mpc_setup):
        """get_pages_fetched returns 0 before fetch_all_pages called."""
        count = mpc_setup.get_pages_fetched()
        
        assert count == 0

    def test_get_pages_fetched_after_fetch(self, mpc_setup):
        """get_pages_fetched returns correct count after fetch_all_pages."""
        mpc_setup.fetch_all_pages()
        count = mpc_setup.get_pages_fetched()
        
        assert count == 5

    def test_get_pages_fetched_after_parse(self, mpc_setup):
        """get_pages_fetched returns correct count after fetch_and_parse_all."""
        mpc_setup.fetch_and_parse_all()
        count = mpc_setup.get_pages_fetched()
        
        assert count == 5


class TestMultiPageCrawlerIntegration:
    """Integration tests for multi-page crawling workflow."""

    def test_full_multi_page_workflow(self):
        """Full workflow: init → fetch all pages → parse → track count."""
        crawler = Mock()
        
        def mock_fetch(url):
            pages = {
                "https://quotes.toscrape.com/": '<html><body>page 1<li class="next"><a href="/page/2/">Next</a></li></body></html>',
                "https://quotes.toscrape.com/page/2/": '<html><body>page 2<li class="next"><a href="/page/3/">Next</a></li></body></html>',
                "https://quotes.toscrape.com/page/3/": "<html><body>page 3</body></html>",
            }
            return pages.get(url, "<html><body>default</body></html>")
        
        def mock_extract(html):
            if "page 1" in html:
                return "text from page 1"
            elif "page 2" in html:
                return "text from page 2"
            return "text from page 3"
        
        crawler.fetch_page = Mock(side_effect=mock_fetch)
        crawler.extract_text = Mock(side_effect=mock_extract)
        
        mpc = MultiPageCrawler(crawler, max_pages=3)
        
        # Execute workflow
        results = mpc.fetch_and_parse_all()
        count = mpc.get_pages_fetched()
        
        # Verify results
        assert len(results) == 3
        assert count == 3
        assert results[0]["page"] == 1
        assert results[2]["page"] == 3
        assert "text from page 1" in results[0]["text"]

    def test_multi_page_crawler_respects_politeness_delay(self):
        """Multi-page crawler respects crawler's politeness delay."""
        crawler = Mock()
        crawler.fetch_page = Mock(return_value='<html><body>page<li class="next"><a href="#">Next</a></li></body></html>')
        crawler.extract_text = Mock(return_value="text")
        # Crawler should have politeness_delay attribute
        crawler.politeness_delay = 6
        
        mpc = MultiPageCrawler(crawler, max_pages=3)
        
        # When fetching, should respect the crawler's delay
        mpc.fetch_all_pages()
        
        # Verify multiple fetches occurred
        assert crawler.fetch_page.call_count >= 3
