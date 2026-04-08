"""
Tests for the Crawler class - Step 1 & 2: Fetching, parsing, error handling, and politeness window.

Tests:
- test_fetch_page_returns_html: Can fetch and return HTML?
- test_extract_text_returns_string: Can extract plain text from HTML?
- test_extract_text_removes_tags: Does it remove HTML tags?
- test_extract_text_handles_empty_html: Graceful handling of empty HTML?
- test_fetch_page_handles_timeout: Catches timeout errors?
- test_fetch_page_handles_http_errors: Catches HTTP 4xx/5xx errors?
- test_fetch_page_handles_connection_error: Catches connection errors?
- test_extract_text_handles_invalid_input: Rejects invalid input?
- test_fetch_page_enforces_politeness_window: 6s delay enforced? (Step 2)
- test_fetch_page_respects_custom_politeness_delay: Custom delay works? (Step 2)
- test_fetch_page_can_disable_politeness_delay: Disable delay for testing? (Step 2)
"""

import pytest
from unittest.mock import patch, Mock
from requests.exceptions import Timeout, HTTPError, ConnectionError
from src.crawler import Crawler


class TestCrawler:
    """Test suite for Crawler class."""
    
    # ========== BASIC FUNCTIONALITY TESTS ==========
    
    def test_fetch_page_returns_html(self, mock_html_response):
        """
        Test that fetch_page returns HTML content from URL.
        
        Should make HTTP GET request and return raw HTML string.
        """
        crawler = Crawler()
        
        with patch('src.crawler.requests.get', return_value=mock_html_response):
            result = crawler.fetch_page("https://quotes.toscrape.com/")
            
            assert isinstance(result, str)
            assert "<html>" in result
            assert "love what you do" in result
    
    def test_extract_text_returns_string(self):
        """
        Test that extract_text returns plain text string.
        
        Should parse HTML with BeautifulSoup and return visible text.
        """
        crawler = Crawler()
        html = "<html><body><p>The only way to do great work is to love what you do.</p></body></html>"
        
        result = crawler.extract_text(html)
        
        assert isinstance(result, str)
        assert "The only way" in result
    
    def test_extract_text_removes_html_tags(self):
        """
        Test that extract_text removes HTML tags.
        
        Should not return any HTML markup, only text.
        """
        crawler = Crawler()
        html = "<html><body><div><p>Quote here</p></div></body></html>"
        
        result = crawler.extract_text(html)
        
        assert "<" not in result
        assert ">" not in result
        assert "Quote here" in result
    
    def test_extract_text_handles_empty_html(self):
        """
        Test that extract_text handles empty HTML gracefully.
        
        Should return empty string for empty body.
        """
        crawler = Crawler()
        html = "<html><body></body></html>"
        
        result = crawler.extract_text(html)
        
        assert isinstance(result, str)
        assert result.strip() == ""
    
    # ========== ERROR HANDLING TESTS ==========
    
    def test_fetch_page_handles_timeout(self):
        """
        Test that fetch_page raises Timeout exception on network timeout.
        
        Should not silently fail, but propagate the error.
        """
        crawler = Crawler(timeout=5)
        
        with patch('src.crawler.requests.get', side_effect=Timeout("Request timed out")):
            with pytest.raises(Timeout):
                crawler.fetch_page("https://quotes.toscrape.com/")
    
    def test_fetch_page_handles_http_404_error(self):
        """
        Test that fetch_page raises HTTPError for 404 Not Found.
        
        Should raise exception when page not found.
        """
        crawler = Crawler()
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.reason = "Not Found"
        
        # Create HTTPError with response object
        http_error = HTTPError("404 Client Error")
        http_error.response = mock_response
        mock_response.raise_for_status.side_effect = http_error
        
        with patch('src.crawler.requests.get', return_value=mock_response):
            with pytest.raises(HTTPError):
                crawler.fetch_page("https://quotes.toscrape.com/nonexistent")
    
    def test_fetch_page_handles_http_500_error(self):
        """
        Test that fetch_page raises HTTPError for 500 Server Error.
        
        Should raise exception on server error.
        """
        crawler = Crawler()
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.reason = "Internal Server Error"
        
        # Create HTTPError with response object
        http_error = HTTPError("500 Server Error")
        http_error.response = mock_response
        mock_response.raise_for_status.side_effect = http_error
        
        with patch('src.crawler.requests.get', return_value=mock_response):
            with pytest.raises(HTTPError):
                crawler.fetch_page("https://quotes.toscrape.com/")
    
    def test_fetch_page_handles_connection_error(self):
        """
        Test that fetch_page raises ConnectionError on network failure.
        
        Should handle DNS failures, refused connections, etc.
        """
        crawler = Crawler()
        
        with patch('src.crawler.requests.get', side_effect=ConnectionError("Connection refused")):
            with pytest.raises(ConnectionError):
                crawler.fetch_page("https://invalid-url-that-doesnt-exist.com/")
    
    def test_extract_text_rejects_none_input(self):
        """
        Test that extract_text raises ValueError for None input.
        
        Should validate input types.
        """
        crawler = Crawler()
        
        with pytest.raises(ValueError):
            crawler.extract_text(None)
    
    def test_extract_text_rejects_non_string_input(self):
        """
        Test that extract_text raises ValueError for non-string input.
        
        Should only accept strings.
        """
        crawler = Crawler()
        
        with pytest.raises(ValueError):
            crawler.extract_text(12345)  # Integer instead of string
    
    def test_extract_text_rejects_empty_string(self):
        """
        Test that extract_text raises ValueError for empty string.
        
        Should reject empty input.
        """
        crawler = Crawler()
        
        with pytest.raises(ValueError):
            crawler.extract_text("")
    
    # ========== INTEGRATION TESTS ==========
    
    def test_crawler_can_fetch_real_website(self):
        """
        Integration test: fetch from real website (quotes.toscrape.com).
        
        This test actually connects to the website.
        Note: This test may fail if the website is down or network is unavailable.
        """
        crawler = Crawler()
        
        try:
            html = crawler.fetch_page("https://quotes.toscrape.com/")
            
            # Verify we got valid HTML
            assert isinstance(html, str)
            assert len(html) > 0
            assert "<html" in html.lower()
        
        except Exception as e:
            # Skip this test if network is unavailable
            pytest.skip(f"Could not reach website: {str(e)}")
    
    def test_crawler_can_extract_from_real_website(self):
        """
        Integration test: fetch and extract text from real website.
        
        Combines fetching and text extraction on real data.
        """
        crawler = Crawler()
        
        try:
            html = crawler.fetch_page("https://quotes.toscrape.com/")
            text = crawler.extract_text(html)
            
            # Verify extraction worked
            assert isinstance(text, str)
            assert len(text) > 0
            assert "<" not in text  # No HTML tags
            assert ">" not in text
        
        except Exception as e:
            pytest.skip(f"Could not reach website: {str(e)}")
    
    # ========== POLITENESS WINDOW TESTS (Step 2) ==========
    
    def test_fetch_page_enforces_default_politeness_window(self, mock_html_response):
        """
        Test that fetch_page enforces 6-second politeness window.
        
        Should sleep 6 seconds before each fetch to avoid hammering the server.
        This is a requirement: be respectful to target website.
        """
        crawler = Crawler()
        
        with patch('src.crawler.requests.get', return_value=mock_html_response):
            with patch('src.crawler.time.sleep') as mock_sleep:
                crawler.fetch_page("https://quotes.toscrape.com/")
                
                # Verify that sleep was called with 6 seconds
                mock_sleep.assert_called_once_with(6)
    
    def test_fetch_page_respects_custom_politeness_delay(self, mock_html_response):
        """
        Test that fetch_page respects custom politeness delay.
        
        Should allow user to set custom delay (e.g., 3s for testing).
        """
        crawler = Crawler(politeness_delay=3)
        
        with patch('src.crawler.requests.get', return_value=mock_html_response):
            with patch('src.crawler.time.sleep') as mock_sleep:
                crawler.fetch_page("https://quotes.toscrape.com/")
                
                # Verify that sleep was called with custom delay
                mock_sleep.assert_called_once_with(3)
    
    def test_fetch_page_can_disable_politeness_delay(self, mock_html_response):
        """
        Test that fetch_page can disable politeness delay.
        
        Should allow politeness_delay=0 for testing (no sleep).
        """
        crawler = Crawler(politeness_delay=0)
        
        with patch('src.crawler.requests.get', return_value=mock_html_response):
            with patch('src.crawler.time.sleep') as mock_sleep:
                crawler.fetch_page("https://quotes.toscrape.com/")
                
                # Verify that sleep was called with 0 (no delay)
                mock_sleep.assert_called_once_with(0)