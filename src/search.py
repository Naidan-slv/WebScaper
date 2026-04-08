"""
Search functionality for querying indexed documents.

Step 4: Basic search to find documents by single word and return results with context.
"""

from src.indexer import Indexer
from src.utils import tokenize


class Search:
    """
    Handles search queries against an indexed document collection.
    
    Provides single-word search with:
    - Document retrieval
    - Result snippets with context
    - Error handling for invalid queries
    """
    
    def __init__(self, indexer: Indexer):
        """
        Initialize Search with an Indexer instance.
        
        Args:
            indexer: Indexer instance containing built inverted index
        
        Raises:
            ValueError: If indexer is None or invalid type
            RuntimeError: If index has not been built
        """
        try:
            # Validate indexer parameter
            if indexer is None:
                raise ValueError("Indexer cannot be None")
            
            if not isinstance(indexer, Indexer):
                raise ValueError(f"Expected Indexer, got {type(indexer).__name__}")
            
            # Check if index has been built (index should be non-empty dict)
            if not hasattr(indexer, 'index') or indexer.index is None:
                raise RuntimeError("Indexer has not been initialized properly")
            
            # For basic check: if documents were added but index is empty, it wasn't built
            if indexer.document_count > 0 and len(indexer.index) == 0:
                raise RuntimeError("Indexer must have build_index() called before Search initialization")
            
            self.indexer = indexer
        
        except (ValueError, RuntimeError) as e:
            raise
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Search: {str(e)}")
    
    def search(self, query: str) -> list:
        """
        Search for documents containing a query word.
        
        Args:
            query: Single word to search for (case-insensitive)
        
        Returns:
            List of document IDs containing the word, or empty list if not found
        
        Raises:
            ValueError: If query is empty or None
            TypeError: If query is not a string
        """
        try:
            # Value validation for None first (before type check)
            if query is None:
                raise ValueError("Query cannot be None")
            
            # Type validation
            if not isinstance(query, str):
                raise TypeError(f"Query must be string, not {type(query).__name__}")
            
            # Value validation for empty string
            if query.strip() == "":
                raise ValueError("Query cannot be empty")
            
            # Search using indexer
            return self.indexer.search(query)
        
        except (ValueError, TypeError) as e:
            raise
        except Exception as e:
            raise RuntimeError(f"Search failed for query '{query}': {str(e)}")
    
    def get_document_text(self, doc_id: int) -> str:
        """
        Retrieve the full text of a document by ID.
        
        Args:
            doc_id: Document ID to retrieve
        
        Returns:
            Full document text
        
        Raises:
            ValueError: If doc_id is invalid or not found
            TypeError: If doc_id is not an integer
        """
        raise NotImplementedError("get_document_text not implemented")
    
    def get_snippet(self, doc_id: int, query: str, context_words: int = 2) -> str:
        """
        Get a snippet of document text with query word and context.
        
        Returns a few words before and after the query word to show context.
        Format: "...word1 word2 QUERY_WORD word3 word4..."
        
        Args:
            doc_id: Document ID to snippet from
            query: Query word to find in document
            context_words: Number of words before/after query to include (default: 2)
        
        Returns:
            Snippet string with query word in context
        
        Raises:
            ValueError: If doc_id invalid, query not found, or context_words negative
            TypeError: If parameters are wrong type
        """
        raise NotImplementedError("get_snippet not implemented")
    
    def search_with_snippets(self, query: str, snippet_context: int = 2) -> list:
        """
        Search for documents and return results with context snippets.
        
        Returns list of dicts: [{"doc_id": id, "snippet": "context text"}, ...]
        
        Args:
            query: Single word to search for
            snippet_context: Number of words before/after for context (default: 2)
        
        Returns:
            List of result dicts with doc_id and snippet, or empty list if no matches
        
        Raises:
            ValueError: If query is empty/None or snippet_context negative
            TypeError: If parameters are wrong type
        """
        raise NotImplementedError("search_with_snippets not implemented")
