"""
Word frequency analyzer for the web scraper search engine.

Phase 2 Step 4: Tracks word frequencies and positions in documents.
Enables ranking and relevance scoring based on term frequency.
"""

from src.utils import tokenize


class WordFrequency:
    """Track word frequencies and positions for ranking."""

    def __init__(self, indexer):
        """
        Initialize word frequency analyzer.
        
        Args:
            indexer (Indexer): Built indexer with documents
            
        Raises:
            ValueError: If indexer is None or not built
        """
        if indexer is None:
            raise ValueError("Indexer cannot be None")
        
        if not indexer.documents or not indexer.index:
            raise ValueError("Indexer must be built with documents and index")
        
        self.indexer = indexer
        self.frequencies = {}  # Will be populated by calculate_frequencies

    def calculate_frequencies(self):
        """
        Calculate frequency of each word in each document.
        
        Returns:
            dict: Format {doc_id: {word: frequency_count}}
            
        Raises:
            RuntimeError: If indexer not initialized
        """
        self.frequencies = {}
        
        # Process each document
        for doc_id, text in self.indexer.documents.items():
            # Tokenize document
            tokens = tokenize(text)
            
            # Count word frequencies
            word_freq = {}
            for word in tokens:
                word_freq[word] = word_freq.get(word, 0) + 1
            
            self.frequencies[doc_id] = word_freq
        
        return self.frequencies

    def get_word_frequency(self, word, doc_id):
        """
        Get frequency of word in specific document.
        
        Args:
            word (str): Word to look up (case-insensitive)
            doc_id (int): Document ID
            
        Returns:
            int: Number of times word appears in document
            
        Raises:
            ValueError: If word or doc_id invalid
            KeyError: If document not found
        """
        raise NotImplementedError

    def get_top_words(self, doc_id, limit=10):
        """
        Get most frequent words in a document.
        
        Args:
            doc_id (int): Document ID
            limit (int): Max words to return
            
        Returns:
            list: [{'word': str, 'frequency': int}, ...] sorted by frequency desc
            
        Raises:
            ValueError: If doc_id invalid
            KeyError: If document not found
        """
        raise NotImplementedError

    def get_document_length(self, doc_id):
        """
        Get total word count in document.
        
        Args:
            doc_id (int): Document ID
            
        Returns:
            int: Total unique + repeated words
            
        Raises:
            KeyError: If document not found
        """
        raise NotImplementedError
