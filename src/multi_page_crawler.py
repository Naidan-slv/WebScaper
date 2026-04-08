"""
Multi-page crawler for the web scraper search engine.

Extends basic crawler to fetch multiple pages from websites.
Handles pagination with politeness delays and error recovery.
"""

from src.crawler import Crawler


class MultiPageCrawler:
    """Fetch and process multiple pages from a website."""

    def __init__(self, crawler, max_pages=10, base_url="https://quotes.toscrape.com"):
        """
        Initialize multi-page crawler.
        
        Args:
            crawler (Crawler): Base crawler instance
            max_pages (int): Maximum pages to fetch
            base_url (str): Base URL for pagination
            
        Raises:
            ValueError: If crawler is None or max_pages invalid
        """
        raise NotImplementedError

    def get_next_page_url(self, current_page):
        """
        Generate URL for next page.
        
        Args:
            current_page (int): Current page number (1-indexed)
            
        Returns:
            str: URL for next page
            
        Raises:
            ValueError: If current_page invalid
        """
        raise NotImplementedError

    def fetch_all_pages(self):
        """
        Fetch all pages up to max_pages.
        
        Returns:
            list: HTML content of each page fetched
            
        Raises:
            RuntimeError: If fetch fails
        """
        raise NotImplementedError

    def fetch_and_parse_all(self):
        """
        Fetch all pages and extract text from each.
        
        Returns:
            list: {"page": int, "text": str, "url": str} for each page
            
        Raises:
            RuntimeError: If fetch/parse fails
        """
        raise NotImplementedError

    def get_pages_fetched(self):
        """
        Get count of pages successfully fetched.
        
        Returns:
            int: Number of pages fetched
        """
        raise NotImplementedError
