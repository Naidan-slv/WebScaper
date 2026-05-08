"""Crawler code for fetching, parsing, and paginating the target website."""

import logging
import time

import requests
from bs4 import BeautifulSoup


logger = logging.getLogger(__name__)


class Crawler:
    """Fetch a page and extract visible text."""

    def __init__(self, timeout: int = 10, politeness_delay: int = 6):
        self.timeout = timeout
        self.politeness_delay = politeness_delay

    def fetch_page(self, url: str) -> str:
        """Fetch a single page, respecting the politeness delay first."""
        time.sleep(self.politeness_delay)

        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.text

        except requests.Timeout:
            logger.error("Request timeout for %s (exceeded %ss)", url, self.timeout)
            raise

        except requests.HTTPError as e:
            logger.error("HTTP %s for %s: %s", e.response.status_code, url, e.response.reason)
            raise

        except requests.ConnectionError as e:
            logger.error("Connection error for %s: %s", url, str(e))
            raise

        except requests.RequestException as e:
            logger.error("Request failed for %s: %s", url, str(e))
            raise

    def extract_text(self, html: str) -> str:
        """Extract visible text from an HTML string."""
        try:
            if not html or not isinstance(html, str):
                raise ValueError("HTML content must be a non-empty string")

            soup = BeautifulSoup(html, "html.parser")
            for tag in soup.find_all(["script", "style"]):
                tag.decompose()

            return soup.get_text(separator=" ", strip=True)

        except Exception as e:
            logger.error("Failed to parse HTML: %s", str(e))
            raise


class MultiPageCrawler:
    """Fetch and parse paginated pages from quotes.toscrape.com."""

    def __init__(self, crawler, max_pages=10, base_url="https://quotes.toscrape.com"):
        if crawler is None:
            raise ValueError("Crawler instance cannot be None")
        if max_pages <= 0:
            raise ValueError("max_pages must be greater than 0")

        self.crawler = crawler
        self.max_pages = max_pages
        self.base_url = base_url
        self.pages_fetched = 0

    def get_next_page_url(self, current_page):
        """Generate the URL for a 1-indexed page number."""
        if current_page <= 0:
            raise ValueError("Page number must be greater than 0")

        if current_page == 1:
            return self.base_url + "/"
        return self.base_url + f"/page/{current_page}/"

    def has_next_page(self, html):
        """Return True if the page contains the site pagination next link."""
        soup = BeautifulSoup(html, "html.parser")
        return soup.find("li", class_="next") is not None

    def fetch_all_pages(self):
        """Fetch pages up to max_pages, stopping at the last site page."""
        pages = []

        try:
            for page_num in range(1, self.max_pages + 1):
                url = self.get_next_page_url(page_num)
                html = self.crawler.fetch_page(url)
                pages.append(html)
                self.pages_fetched += 1

                if not self.has_next_page(html):
                    break
        except Exception as e:
            raise RuntimeError(f"Failed to fetch pages: {str(e)}")

        return pages

    def fetch_and_parse_all(self):
        """Fetch all pages and return page number, text, and URL for each."""
        results = []
        pages_html = self.fetch_all_pages()

        try:
            for page_num, html in enumerate(pages_html, start=1):
                results.append({
                    "page": page_num,
                    "text": self.crawler.extract_text(html),
                    "url": self.get_next_page_url(page_num),
                })
        except Exception as e:
            raise RuntimeError(f"Failed to parse pages: {str(e)}")

        return results

    def get_pages_fetched(self):
        return self.pages_fetched
