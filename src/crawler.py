"""
Web crawler for fetching and parsing website content.

Step 1: Basic crawler to fetch a single page and extract text.
"""

import requests
from bs4 import BeautifulSoup


class Crawler:
    """
    Simple web crawler that fetches pages and extracts text.
    """
    
    def fetch_page(self, url: str) -> str:
        """
        Fetch a single page from a URL.
        
        Args:
            url: URL to fetch
        
        Returns:
            HTML content of the page as string
        
        Raises:
            requests.RequestException: If network request fails
        """
        pass
    
    def extract_text(self, html: str) -> str:
        """
        Extract plain text from HTML content.
        
        Args:
            html: HTML content to parse
        
        Returns:
            Extracted plain text
        """
        pass
