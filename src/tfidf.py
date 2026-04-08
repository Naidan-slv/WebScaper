"""
TF-IDF (Term Frequency - Inverse Document Frequency) ranking.

Ranks search results by relevance using the TF-IDF algorithm:
  TF(t,d)  = count of term t in document d / total words in document d
  IDF(t)   = log(total documents / documents containing term t)
  TF-IDF   = TF * IDF

Higher scores mean the term is more relevant to that specific document.
"""

import math
from src.utils import tokenize


class TfIdf:
    """Rank search results using TF-IDF scoring."""

    def __init__(self, indexer):
        """
        Initialize TF-IDF ranker with a built Indexer.

        Args:
            indexer: Indexer instance with documents and built index.

        Raises:
            ValueError: If indexer is None or not built.
        """
        if indexer is None:
            raise ValueError("Indexer cannot be None")
        if not indexer.index:
            raise ValueError("Indexer must have a built index")
        if not indexer.documents:
            raise ValueError("Indexer must have documents")

        self.indexer = indexer

    def calculate_tf(self, word, doc_id):
        """
        Calculate term frequency of a word in a document.

        TF = occurrences of word in doc / total words in doc

        Args:
            word (str): The term (case-insensitive).
            doc_id (int): Document ID.

        Returns:
            float: Term frequency (0.0 to 1.0).

        Raises:
            KeyError: If doc_id not found.
        """
        if doc_id not in self.indexer.documents:
            raise KeyError(f"Document {doc_id} not found")

        text = self.indexer.documents[doc_id]
        tokens = tokenize(text)
        if not tokens:
            return 0.0

        word_lower = word.lower().strip()
        count = tokens.count(word_lower)
        return count / len(tokens)

    def calculate_idf(self, word):
        """
        Calculate inverse document frequency of a word.

        IDF = log(total documents / documents containing word)
        Returns 0.0 if word not in index.

        Args:
            word (str): The term (case-insensitive).

        Returns:
            float: Inverse document frequency (>= 0.0).
        """
        word_lower = word.lower().strip()
        if word_lower not in self.indexer.index:
            return 0.0

        docs_containing = len(self.indexer.index[word_lower])
        total_docs = self.indexer.document_count
        return math.log(total_docs / docs_containing)

    def calculate_tfidf(self, word, doc_id):
        """
        Calculate TF-IDF score for a word in a document.

        TF-IDF = TF(word, doc) * IDF(word)

        Args:
            word (str): The term.
            doc_id (int): Document ID.

        Returns:
            float: TF-IDF score (>= 0.0).

        Raises:
            KeyError: If doc_id not found.
        """
        return self.calculate_tf(word, doc_id) * self.calculate_idf(word)

    def rank_documents(self, query):
        """
        Rank all matching documents for a query by TF-IDF score.

        For multi-word queries, sums TF-IDF scores across all query terms.

        Args:
            query (str): Search query (single or multi-word).

        Returns:
            list: [{'doc_id': int, 'score': float}, ...] sorted by score descending.

        Raises:
            ValueError: If query is None or empty.
        """
        if query is None:
            raise ValueError("Query cannot be None")
        if not query.strip():
            raise ValueError("Query cannot be empty")

        words = tokenize(query)
        scores = {}

        for word in words:
            if word not in self.indexer.index:
                continue
            for doc_id in self.indexer.index[word]:
                if doc_id not in scores:
                    scores[doc_id] = 0.0
                scores[doc_id] += self.calculate_tfidf(word, doc_id)

        results = [
            {"doc_id": doc_id, "score": score}
            for doc_id, score in scores.items()
            if score > 0.0
        ]
        results.sort(key=lambda r: r["score"], reverse=True)
        return results

    def search(self, query, limit=10):
        """
        Search and return ranked results with scores and snippets.

        Args:
            query (str): Search query.
            limit (int): Max results to return.

        Returns:
            list: [{'doc_id': int, 'score': float, 'snippet': str}, ...]
                  sorted by score descending.

        Raises:
            ValueError: If query is None or empty.
        """
        raise NotImplementedError
