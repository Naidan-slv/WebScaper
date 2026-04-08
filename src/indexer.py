"""
Inverted index for searching through crawled documents.

Step 3: Basic indexer to build an inverted index from documents.
"""

from src.utils import tokenize


class Indexer:
    """
    Builds and manages an inverted index for document search.
    
    Inverted index maps: word -> [list of document IDs containing word]
    This enables fast single-word searches.
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
        Creates mapping: word -> set of document IDs containing word
        """
        # Clear previous index
        self.index = {}
        
        # Process each document
        for doc_id, text in self.documents.items():
            # Tokenize document text
            tokens = tokenize(text)
            
            # Add each unique token to index
            for token in set(tokens):  # set() deduplicates tokens
                if token not in self.index:
                    self.index[token] = set()
                
                self.index[token].add(doc_id)
        
        # Convert sets to sorted lists for consistent output
        for word in self.index:
            self.index[word] = sorted(list(self.index[word]))
    
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
            return self.index[query_normalized]
        else:
            return []
    
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
