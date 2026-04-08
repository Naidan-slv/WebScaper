"""
Web crawler for fetching and parsing website content.

Step 1: Basic crawler to fetch a single page and extract text with error handling.
"""

import requests
from bs4 import BeautifulSoup
import logging

# Configure logging for error tracking
logger = logging.getLogger(__name__)


class Crawler:
    """
    Simple web crawler that fetches pages and extracts text with proper error handling.
    """
    
    def __init__(self, timeout: int = 10):
        """
        Initialize crawler with timeout setting.
        
        Args:
            timeout: Request timeout in seconds (default: 10)
        """
        self.timeout = timeout
    
    def fetch_page(self, url: str) -> str:
        """
        Fetch a single page from a URL with error handling.
        
        Makes HTTP GET request to the URL and returns raw HTML.
        Handles network timeouts, connection errors, and HTTP errors.
        
        Args:
            url: URL to fetch
        
        Returns:
            HTML content of the page as string
        
        Raises:
            requests.Timeout: If request exceeds timeout
            requests.HTTPError: If server returns 4xx/5xx status
            requests.RequestException: If other network errors occur
        """
        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()  # Raise exception for 4xx/5xx status codes
            return response.text
        
        except requests.Timeout:
            error_msg = f"Request timeout for {url} (exceeded {self.timeout}s)"
            logger.error(error_msg)
            raise
        
        except requests.HTTPError as e:
            error_msg = f"HTTP {e.response.status_code} for {url}: {e.response.reason}"
            logger.error(error_msg)
            raise
        
        except requests.ConnectionError as e:
            error_msg = f"Connection error for {url}: {str(e)}"
            logger.error(error_msg)
            raise
        
        except requests.RequestException as e:
            error_msg = f"Request failed for {url}: {str(e)}"
            logger.error(error_msg)
            raise
    
    def extract_text(self, html: str) -> str:
        """
        Extract plain text from HTML content with error handling.
        
        Uses BeautifulSoup to parse HTML and extract only visible text,
        removing all HTML tags and markup. Handles malformed HTML gracefully.
        
        Args:
            html: HTML content to parse
        
        Returns:
            Extracted plain text with HTML tags removed
        
        Raises:
            ValueError: If HTML is None or not a string
        """
        try:
            if not html or not isinstance(html, str):
                raise ValueError("HTML content must be a non-empty string")
            
            soup = BeautifulSoup(html, 'html.parser')
            text = soup.get_text(separator=' ', strip=True)
            return text
        
        except Exception as e:
            error_msg = f"Failed to parse HTML: {str(e)}"
            logger.error(error_msg)
            raise
