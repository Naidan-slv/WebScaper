"""
Inverted index for searching through crawled documents.

Builds a rich inverted index storing frequency and position statistics
for each word in each document.
"""

from src.utils import tokenize


class Indexer:
    """
    Builds and manages an inverted index for document search.
    
    Rich inverted index maps:
        word -> {doc_id: {"frequency": int, "positions": [int, ...]}}
    This enables fast search with relevance statistics.
    """
    
    def __init__(self):
        """Initialize indexer with empty index and document store."""
        self.index = {}  # word -> set of document IDs
        self.documents = {}  # document ID -> original text
        self.document_count = 0
    
    def add_document(self, text: str) -> int:
        """
        Add a document to the indexer.
        
        Args:
            text: Document text to index
        
        Returns:
            Document ID assigned to this document
        """
        doc_id = self.document_count
        self.documents[doc_id] = text
        self.document_count += 1
        return doc_id
    
    def build_index(self) -> None:
        """
        Build the inverted index from all added documents.
        
        Must be called after adding documents and before searching.
        Creates mapping: word -> {doc_id: {"frequency": count, "positions": [indices]}}
        """
        # Clear previous index
        self.index = {}
        
        # Process each document
        for doc_id, text in self.documents.items():
            # Tokenize document text
            tokens = tokenize(text)
            
            # Track frequency and positions for each token
            for position, token in enumerate(tokens):
                if token not in self.index:
                    self.index[token] = {}
                
                if doc_id not in self.index[token]:
                    self.index[token][doc_id] = {"frequency": 0, "positions": []}
                
                self.index[token][doc_id]["frequency"] += 1
                self.index[token][doc_id]["positions"].append(position)
    
    def search(self, query: str) -> list:
        """
        Search for documents containing a word.
        
        Args:
            query: Word to search for (case-insensitive)
        
        Returns:
            List of document IDs containing the word, sorted by ID
        """
        # Normalize query (same tokenization as build_index)
        query_normalized = query.lower().strip()
        
        # Return matching document IDs or empty list
        if query_normalized in self.index:
            return sorted(self.index[query_normalized].keys())
        else:
            return []
    
    def get_index_entry(self, word: str) -> dict:
        """
        Retrieve the full index entry for a word.
        
        Args:
            word: Word to look up (case-insensitive)
        
        Returns:
            dict: {doc_id: {"frequency": int, "positions": [int]}} or None if not found
        """
        word_normalized = word.lower().strip()
        if word_normalized in self.index:
            return self.index[word_normalized]
        return None
    
    def get_document(self, doc_id: int) -> str:
        """
        Retrieve the original text of a document by ID.
        
        Args:
            doc_id: Document ID to retrieve
        
        Returns:
            Document text
        
        Raises:
            KeyError: If document ID not found
        """
        return self.documents[doc_id]
