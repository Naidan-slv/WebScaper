"""
Tests for the Crawler class.

Step 1 Tests:
- test_fetch_page: Can fetch a page and return HTML?
- test_extract_text: Can extract text from HTML?
"""

import pytest
from unittest.mock import Mock, patch
from src.crawler import Crawler


class TestCrawler:
    """Test suite for Crawler class."""
    
    def test_fetch_page_returns_html(self, mock_html_response):
        """
        Test that fetch_page returns HTML content.
        
        Should make HTTP request and return raw HTML.
        """
        # TODO: Implement in Phase 1, Step 1
        pass
    
    def test_extract_text_returns_string(self, mock_html_response):
        """
        Test that extract_text returns plain text string.
        
        Should parse HTML and return visible text.
        """
        # TODO: Implement in Phase 1, Step 1
        pass