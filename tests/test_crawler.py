"""
Tests for the Crawler class - Step 1: Basic fetching and parsing.

Tests:
- test_fetch_page_returns_html: Can fetch and return HTML?
- test_extract_text_returns_string: Can extract plain text from HTML?
- test_extract_text_removes_tags: Does it remove HTML tags?
"""

import pytest
from unittest.mock import patch, Mock
from src.crawler import Crawler


class TestCrawler:
    """Test suite for Crawler class."""
    
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
            assert "Famous Quotes" in result
    
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