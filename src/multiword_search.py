"""
Multi-word search with AND logic for the web scraper search engine.

Provides search functionality for multiple words with AND logic:
- Query: "love life" returns documents containing BOTH words
- More advanced than single-word search
- Combines results from multiple single-word searches
"""


class MultiwordSearch:
    """Execute multi-word queries with AND logic over the inverted index."""

    def __init__(self, search):
        """
        Initialize multi-word search with Search instance.
        
        Args:
            search: Search instance (single-word searcher)
            
        Raises:
            ValueError: If search is None or not built
        """
        if search is None:
            raise ValueError("Search instance cannot be None")
        
        # Verify search has indexer and it's built
        if not hasattr(search, "indexer"):
            raise RuntimeError("Search must have indexer attribute")
        if not search.indexer or not search.indexer.index:
            raise RuntimeError("Search indexer must be built before MultiwordSearch")
        
        self.search = search

    def search_and(self, query):
        """
        Search for documents containing ALL words in query (AND logic).
        
        Args:
            query (str): Multi-word query e.g., "love life wisdom"
            
        Returns:
            list: Document IDs containing all words
            
        Raises:
            ValueError: If query invalid
            RuntimeError: If search not initialized
        """
        raise NotImplementedError

    def search_and_with_snippets(self, query, context_words=5):
        """
        Search for documents with ALL words, return with snippets.
        
        Args:
            query (str): Multi-word query
            context_words (int): Words of context around match
            
        Returns:
            list: Results with format [{'doc_id': int, 'snippet': str, 'text': str}, ...]
            
        Raises:
            ValueError: If query invalid
            RuntimeError: If search not initialized
        """
        raise NotImplementedError

    def search_or(self, query):
        """
        Search for documents containing ANY word in query (OR logic).
        
        Args:
            query (str): Multi-word query
            
        Returns:
            list: Document IDs containing any words
            
        Raises:
            ValueError: If query invalid
            RuntimeError: If search not initialized
        """
        raise NotImplementedError

    def get_intersection(self, result_sets):
        """
        Get intersection of multiple result sets (AND logic).
        
        Args:
            result_sets (list): List of document ID lists
            
        Returns:
            set: Document IDs in all sets
        """
        raise NotImplementedError

    def get_union(self, result_sets):
        """
        Get union of multiple result sets (OR logic).
        
        Args:
            result_sets (list): List of document ID lists
            
        Returns:
            set: Document IDs in any set
        """
        raise NotImplementedError

    def tokenize_query(self, query):
        """
        Break query into individual words.
        
        Args:
            query (str): Multi-word query string
            
        Returns:
            list: Individual lowercase words
            
        Raises:
            ValueError: If query invalid
        """
        raise NotImplementedError
