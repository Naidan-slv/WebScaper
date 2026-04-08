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
        
        Makes HTTP GET request to the URL and returns raw HTML.
        
        Args:
            url: URL to fetch
        
        Returns:
            HTML content of the page as string
        
        Raises:
            requests.RequestException: If network request fails
        """
        response = requests.get(url)
        response.raise_for_status()  # Raise exception for 4xx/5xx status codes
        return response.text
    
    def extract_text(self, html: str) -> str:
        """
        Extract plain text from HTML content.
        
        Uses BeautifulSoup to parse HTML and extract only visible text,
        removing all HTML tags and markup.
        
        Args:
            html: HTML content to parse
        
        Returns:
            Extracted plain text with HTML tags removed
        """
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)
        return text
