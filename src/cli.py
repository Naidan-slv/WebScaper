"""
Basic CLI for the web scraper search engine.

Provides a command-line interface to:
- Build an inverted index from a website
- Search the index with queries
- Display results with context snippets
"""


class CLI:
    """Command-line interface for web scraper search engine."""

    def __init__(self, crawler, indexer, search):
        """
        Initialize CLI with crawler, indexer, and search components.
        
        Args:
            crawler: Crawler instance for fetching pages
            indexer: Indexer instance for building search index
            search: Search instance for executing queries
            
        Raises:
            ValueError: If any component is None
            RuntimeError: If indexer is not built
        """
        if crawler is None:
            raise ValueError("Crawler cannot be None")
        if indexer is None:
            raise ValueError("Indexer cannot be None")
        if search is None:
            raise ValueError("Search cannot be None")
        
        # Check if indexer has been built
        if not hasattr(indexer, "index"):
            raise RuntimeError("Indexer must have index attribute")
        if not indexer.index:
            raise RuntimeError("Indexer must be built before initializing CLI")
        
        self.crawler = crawler
        self.indexer = indexer
        self.search = search

    def build_index(self, url):
        """
        Fetch pages from URL and build search index.
        
        Args:
            url (str): Website URL to scrape and index
            
        Returns:
            int: Number of documents indexed
            
        Raises:
            ValueError: If URL is invalid or indexer fails to build
            Exception: If crawler fails to fetch pages
        """
        raise NotImplementedError

    def search_query(self, query):
        """
        Execute search query and return results with snippets.
        
        Args:
            query (str): Search query (single or multiple words)
            
        Returns:
            list: Results with format [{'doc_id': int, 'snippet': str, 'text': str}, ...]
            
        Raises:
            ValueError: If query is invalid
        """
        raise NotImplementedError

    def display_results(self, query, results):
        """
        Format and display search results to console.
        
        Args:
            query (str): Original search query
            results (list): Results from search_query()
            
        Returns:
            str: Formatted output string
        """
        raise NotImplementedError

    def run(self):
        """
        Run interactive REPL for user queries.
        
        Workflow:
        1. Prompt user for website URL
        2. Build index
        3. Loop: Accept queries, display results
        4. Exit on "quit" or EOF
        """
        raise NotImplementedError
