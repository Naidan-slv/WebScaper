"""
Web crawler for fetching and parsing website content.

Step 1: Basic crawler to fetch a single page and extract text with error handling.Step 2: Add politeness window to respect target website (6-second delay between requests)."""

import requests
from bs4 import BeautifulSoup
import logging
import time

# Configure logging for error tracking
logger = logging.getLogger(__name__)


class Crawler:
    """
    Simple web crawler that fetches pages and extracts text with proper error handling.
    Includes politeness window to respect target website.
    """
    
    def __init__(self, timeout: int = 10, politeness_delay: int = 6):
        """
        Initialize crawler with timeout and politeness delay settings.
        
        Args:
            timeout: Request timeout in seconds (default: 10)
            politeness_delay: Seconds to sleep before each fetch (default: 6)
                             Set to 0 to disable politeness window
        """
        self.timeout = timeout
        self.politeness_delay = politeness_delay
    
    def fetch_page(self, url: str) -> str:
        """
        Fetch a single page from a URL with error handling and politeness window.
        
        Makes HTTP GET request to the URL and returns raw HTML.
        Sleeps before each request to respect target website (politeness window).
        Handles network timeouts, connection errors, and HTTP errors.
        
        Args:
            url: URL to fetch
        
        Returns:
            HTML content of the page as string
        
        Raises:
            requests.Timeout: If request exceeds timeout
            requests.HTTPError: If server returns 4xx/5xx status
            requests.RequestException: If other network errors occur
        
        Note:
            Sleeps for politeness_delay seconds before fetching to avoid
            overwhelming the target server. This is respectful web scraping practice.
        """
        # Enforce politeness window: sleep before fetch to avoid hammering server
        time.sleep(self.politeness_delay)
        
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
