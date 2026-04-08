"""
Command-line interface for the Search Engine Tool.

Implements the 4 required commands from the COMP3011 coursework brief:
  > build   - Crawl website, build index, save to file
  > load    - Load previously saved index from file
  > print   - Print inverted index for a word
  > find    - Find pages containing search terms
"""

import os
from src.crawler import Crawler
from src.indexer import Indexer
from src.search import Search
from src.multi_page_crawler import MultiPageCrawler
from src.multiword_search import MultiwordSearch
from src.word_frequency import WordFrequency
from src.persistence import Persistence


# Default paths for index storage
DEFAULT_INDEX_DIR = "data"
DEFAULT_INDEX_FILE = os.path.join(DEFAULT_INDEX_DIR, "index.json")
DEFAULT_DOCS_FILE = os.path.join(DEFAULT_INDEX_DIR, "documents.json")
BASE_URL = "https://quotes.toscrape.com/"


class CLI:
    """Command-line interface for the search engine tool."""

    def __init__(self):
        """Initialize CLI with no components loaded yet."""
        self.crawler = Crawler(timeout=15, politeness_delay=6)
        self.indexer = Indexer()
        self.search = None
        self.multiword_search = None
        self.word_freq = None
        self.persistence = None
        self.is_built = False

    def build(self, max_pages=10):
        """
        Crawl the website, build the index, and save to file system.

        Implements: > build

        Args:
            max_pages: Maximum number of pages to crawl (default 10)

        Returns:
            dict: Summary with pages_crawled, words_indexed, docs_stored
        """
        raise NotImplementedError

    def load(self):
        """
        Load a previously saved index from the file system.

        Implements: > load

        Returns:
            dict: Summary with words_loaded, docs_loaded

        Raises:
            FileNotFoundError: If index files don't exist
        """
        raise NotImplementedError

    def print_index(self, word):
        """
        Print the inverted index entry for a given word.

        Implements: > print <word>

        Args:
            word: The word to look up in the index

        Returns:
            dict or None: Index entry for the word, or None if not found
        """
        raise NotImplementedError

    def find(self, query):
        """
        Find pages containing the given search terms.

        Implements: > find <query>

        Args:
            query: Search query (single or multiple words)

        Returns:
            list: Search results with doc_ids and snippets
        """
        raise NotImplementedError

    def _wire_search_components(self):
        """Set up search, multiword search, and word frequency after indexing."""
        self.search = Search(self.indexer)
        self.multiword_search = MultiwordSearch(self.search)
        self.word_freq = WordFrequency(self.indexer)
        self.word_freq.calculate_frequencies()
        self.is_built = True

    def run(self):
        """
        Run the interactive command-line shell.

        Commands:
            build       - Crawl website and build index
            load        - Load saved index from file
            print <w>   - Print inverted index for word
            find <q>    - Find pages with search terms
            help        - Show available commands
            quit/exit   - Exit the program
        """
        raise NotImplementedError

    def _print_help(self):
        """Print available commands."""
        raise NotImplementedError
