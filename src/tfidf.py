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

        Uses smoothed IDF: log(1 + N / df) to ensure words appearing in all
        documents still receive a small positive score. This is important for
        small corpora where many words appear in every document.

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
        return math.log(1 + total_docs / docs_containing)

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

    def rank_documents_and(self, query):
        """
        Rank documents that contain ALL query terms, scored by TF-IDF.

        For multi-word queries, only documents containing every term are
        included. Scores are summed across all query terms.

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

        # Find docs that contain ALL words (intersection)
        doc_sets = []
        for word in words:
            if word not in self.indexer.index:
                return []  # A word has no matches → AND result is empty
            doc_sets.append(set(self.indexer.index[word].keys()))

        common_docs = doc_sets[0]
        for s in doc_sets[1:]:
            common_docs &= s

        if not common_docs:
            return []

        # Score the common docs by summing TF-IDF across all query terms
        results = []
        for doc_id in common_docs:
            score = sum(self.calculate_tfidf(word, doc_id) for word in words)
            if score > 0.0:
                results.append({"doc_id": doc_id, "score": score})

        results.sort(key=lambda r: r["score"], reverse=True)
        return results

    def rank_phrase(self, phrase):
        """Rank documents containing an exact phrase using word positions."""
        if phrase is None:
            raise ValueError("Phrase cannot be None")

        words = tokenize(phrase)
        if not words:
            raise ValueError("Phrase cannot be empty")
        if len(words) == 1:
            return self.rank_documents_and(words[0])

        doc_sets = []
        for word in words:
            if word not in self.indexer.index:
                return []
            doc_sets.append(set(self.indexer.index[word].keys()))

        common_docs = doc_sets[0]
        for s in doc_sets[1:]:
            common_docs &= s

        results = []
        for doc_id in common_docs:
            positions = self._phrase_positions(words, doc_id)
            if not positions:
                continue

            # Repeated exact phrases should rank higher than one-off matches.
            base_score = sum(self.calculate_tfidf(word, doc_id) for word in words)
            score = base_score * len(positions)
            if score > 0.0:
                results.append({
                    "doc_id": doc_id,
                    "score": score,
                    "positions": positions,
                    "phrase_frequency": len(positions),
                })

        results.sort(key=lambda r: (-r["score"], r["doc_id"]))
        return results

    def _phrase_positions(self, words, doc_id):
        """Return starting positions where all phrase words appear consecutively."""
        first_positions = self.indexer.index[words[0]][doc_id]["positions"]
        other_positions = [
            set(self.indexer.index[word][doc_id]["positions"])
            for word in words[1:]
        ]

        starts = []
        for start in first_positions:
            if all(start + offset in other_positions[offset - 1]
                   for offset in range(1, len(words))):
                starts.append(start)

        return starts

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
        if query is None:
            raise ValueError("Query cannot be None")

        ranked = self.rank_documents(query)
        results = []
        for r in ranked[:limit]:
            snippet = self.indexer.documents.get(r["doc_id"], "")[:100]
            results.append({
                "doc_id": r["doc_id"],
                "score": r["score"],
                "snippet": snippet,
            })
        return results
