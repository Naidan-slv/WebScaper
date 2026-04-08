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
        if query is None:
            raise ValueError("Query cannot be None")
        
        # Tokenize query into words
        words = self.tokenize_query(query)
        
        # Search for each word and collect results
        result_sets = []
        for word in words:
            # search() returns list of doc_ids (ints)
            doc_ids = self.search.search(word)
            result_sets.append(doc_ids)
        
        # Get intersection of all result sets (AND logic)
        common_docs = self.get_intersection(result_sets)
        
        # Return sorted list of document IDs
        return sorted(list(common_docs))

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
        if query is None:
            raise ValueError("Query cannot be None")
        
        # Tokenize query into words
        words = self.tokenize_query(query)
        
        # Get documents containing all words
        doc_ids = self.search_and(query)
        
        # For each matching document, get snippets for the first word
        # (all words are in the document, so snippet for first word is sufficient)
        results = []
        if doc_ids and words:
            first_word = words[0]
            # Use search_with_snippets from search component which returns
            # results with 'doc_id', 'snippet', 'text' keys
            for doc_id in doc_ids:
                try:
                    # Get the document text
                    doc_text = self.search.get_document_text(doc_id)
                    # Get snippet for first word
                    snippet = self.search.get_snippet(doc_id, first_word, context_words)
                    results.append({
                        "doc_id": doc_id,
                        "snippet": snippet,
                        "text": doc_text
                    })
                except (ValueError, RuntimeError):
                    # Skip if document not found
                    continue
        
        return results

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
        if query is None:
            raise ValueError("Query cannot be None")
        
        # Tokenize query into words
        words = self.tokenize_query(query)
        
        # Search for each word and collect results
        result_sets = []
        for word in words:
            # search() returns list of doc_ids (ints)
            doc_ids = self.search.search(word)
            result_sets.append(doc_ids)
        
        # Get union of all result sets (OR logic)
        any_docs = self.get_union(result_sets)
        
        # Return sorted list of document IDs
        return sorted(list(any_docs))

    def get_intersection(self, result_sets):
        """
        Get intersection of multiple result sets (AND logic).
        
        Args:
            result_sets (list): List of document ID lists
            
        Returns:
            set: Document IDs in all sets
        """
        if not result_sets:
            return set()
        
        # Start with first set, find intersection with all others
        intersection = set(result_sets[0])
        
        for result_set in result_sets[1:]:
            intersection = intersection.intersection(set(result_set))
        
        return intersection

    def get_union(self, result_sets):
        """
        Get union of multiple result sets (OR logic).
        
        Args:
            result_sets (list): List of document ID lists
            
        Returns:
            set: Document IDs in any set
        """
        if not result_sets:
            return set()
        
        # Combine all document IDs from all sets
        union = set()
        
        for result_set in result_sets:
            union = union.union(set(result_set))
        
        return union

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
        if query is None:
            raise ValueError("Query cannot be None")
        
        query = query.strip()
        if not query:
            raise ValueError("Query cannot be empty")
        
        words = query.lower().split()
        return words
