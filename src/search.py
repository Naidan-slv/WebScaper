"""Search, multi-word search, TF-IDF ranking, and phrase matching."""

import math

from src.indexer import Indexer, tokenize


class Search:
    """Basic single-word search with snippets."""

    def __init__(self, indexer: Indexer):
        try:
            if indexer is None:
                raise ValueError("Indexer cannot be None")
            if not isinstance(indexer, Indexer):
                raise ValueError(f"Expected Indexer, got {type(indexer).__name__}")
            if not hasattr(indexer, "index") or indexer.index is None:
                raise RuntimeError("Indexer has not been initialized properly")
            if indexer.document_count > 0 and len(indexer.index) == 0:
                raise RuntimeError("Indexer must have build_index() called before Search initialization")

            self.indexer = indexer

        except (ValueError, RuntimeError) as e:
            raise
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Search: {str(e)}")

    def search(self, query: str) -> list:
        try:
            if query is None:
                raise ValueError("Query cannot be None")
            if not isinstance(query, str):
                raise TypeError(f"Query must be string, not {type(query).__name__}")
            if query.strip() == "":
                raise ValueError("Query cannot be empty")

            return self.indexer.search(query)

        except (ValueError, TypeError) as e:
            raise
        except Exception as e:
            raise RuntimeError(f"Search failed for query '{query}': {str(e)}")

    def get_document_text(self, doc_id: int) -> str:
        try:
            if not isinstance(doc_id, int):
                raise TypeError(f"doc_id must be integer, not {type(doc_id).__name__}")
            if doc_id < 0:
                raise ValueError(f"doc_id must be non-negative, got {doc_id}")
            if doc_id not in self.indexer.documents:
                raise ValueError(f"Document with ID {doc_id} not found")

            return self.indexer.get_document(doc_id)

        except (ValueError, TypeError) as e:
            raise
        except Exception as e:
            raise RuntimeError(f"Failed to retrieve document {doc_id}: {str(e)}")

    def get_snippet(self, doc_id: int, query: str, context_words: int = 2) -> str:
        try:
            if not isinstance(context_words, int):
                raise TypeError(f"context_words must be integer, not {type(context_words).__name__}")
            if context_words < 0:
                raise ValueError(f"context_words must be non-negative, got {context_words}")
            if not isinstance(query, str) or query.strip() == "":
                raise ValueError("Query must be non-empty string")

            tokens = tokenize(self.get_document_text(doc_id))
            query_normalized = query.lower().strip()

            query_index = None
            for i, token in enumerate(tokens):
                if token == query_normalized:
                    query_index = i
                    break

            if query_index is None:
                raise ValueError(f"Word '{query}' not found in document {doc_id}")

            start_index = max(0, query_index - context_words)
            end_index = min(len(tokens), query_index + context_words + 1)
            snippet_tokens = tokens[start_index:end_index]

            if start_index > 0:
                snippet_tokens.insert(0, "...")
            if end_index < len(tokens):
                snippet_tokens.append("...")

            return " ".join(snippet_tokens)

        except (ValueError, TypeError) as e:
            raise
        except Exception as e:
            raise RuntimeError(f"Failed to generate snippet for doc {doc_id}: {str(e)}")

    def search_with_snippets(self, query: str, snippet_context: int = 2) -> list:
        try:
            if not isinstance(snippet_context, int):
                raise TypeError(f"snippet_context must be integer, not {type(snippet_context).__name__}")
            if snippet_context < 0:
                raise ValueError(f"snippet_context must be non-negative, got {snippet_context}")

            doc_ids = self.search(query)
            if not doc_ids:
                return []

            results = []
            for doc_id in doc_ids:
                try:
                    results.append({
                        "doc_id": doc_id,
                        "snippet": self.get_snippet(doc_id, query, context_words=snippet_context),
                    })
                except (ValueError, TypeError, RuntimeError):
                    continue

            return results

        except (ValueError, TypeError) as e:
            raise
        except Exception as e:
            raise RuntimeError(f"Search with snippets failed for query '{query}': {str(e)}")


class MultiwordSearch:
    """Execute multi-word queries over the inverted index."""

    def __init__(self, search):
        if search is None:
            raise ValueError("Search instance cannot be None")
        if not hasattr(search, "indexer"):
            raise RuntimeError("Search must have indexer attribute")
        if not search.indexer or not search.indexer.index:
            raise RuntimeError("Search indexer must be built before MultiwordSearch")

        self.search = search

    def search_and(self, query):
        if query is None:
            raise ValueError("Query cannot be None")

        result_sets = [self.search.search(word) for word in self.tokenize_query(query)]
        return sorted(list(self.get_intersection(result_sets)))

    def search_and_with_snippets(self, query, context_words=5):
        if query is None:
            raise ValueError("Query cannot be None")

        words = self.tokenize_query(query)
        doc_ids = self.search_and(query)
        results = []

        if doc_ids and words:
            first_word = words[0]
            for doc_id in doc_ids:
                try:
                    results.append({
                        "doc_id": doc_id,
                        "snippet": self.search.get_snippet(doc_id, first_word, context_words),
                        "text": self.search.get_document_text(doc_id),
                    })
                except (ValueError, RuntimeError):
                    continue

        return results

    def search_or(self, query):
        if query is None:
            raise ValueError("Query cannot be None")

        result_sets = [self.search.search(word) for word in self.tokenize_query(query)]
        return sorted(list(self.get_union(result_sets)))

    def get_intersection(self, result_sets):
        if not result_sets:
            return set()

        intersection = set(result_sets[0])
        for result_set in result_sets[1:]:
            intersection &= set(result_set)
        return intersection

    def get_union(self, result_sets):
        if not result_sets:
            return set()

        union = set()
        for result_set in result_sets:
            union |= set(result_set)
        return union

    def tokenize_query(self, query):
        if query is None:
            raise ValueError("Query cannot be None")

        query = query.strip()
        if not query:
            raise ValueError("Query cannot be empty")

        return query.lower().split()


class TfIdf:
    """Rank search results using TF-IDF scoring."""

    def __init__(self, indexer):
        if indexer is None:
            raise ValueError("Indexer cannot be None")
        if not indexer.index:
            raise ValueError("Indexer must have a built index")
        if not indexer.documents:
            raise ValueError("Indexer must have documents")

        self.indexer = indexer

    def calculate_tf(self, word, doc_id):
        if doc_id not in self.indexer.documents:
            raise KeyError(f"Document {doc_id} not found")

        tokens = tokenize(self.indexer.documents[doc_id])
        if not tokens:
            return 0.0

        return tokens.count(word.lower().strip()) / len(tokens)

    def calculate_idf(self, word):
        word_lower = word.lower().strip()
        if word_lower not in self.indexer.index:
            return 0.0

        docs_containing = len(self.indexer.index[word_lower])
        total_docs = self.indexer.document_count
        return math.log(1 + total_docs / docs_containing)

    def calculate_tfidf(self, word, doc_id):
        return self.calculate_tf(word, doc_id) * self.calculate_idf(word)

    def rank_documents(self, query):
        if query is None:
            raise ValueError("Query cannot be None")
        if not query.strip():
            raise ValueError("Query cannot be empty")

        scores = {}
        for word in tokenize(query):
            if word not in self.indexer.index:
                continue
            for doc_id in self.indexer.index[word]:
                scores[doc_id] = scores.get(doc_id, 0.0) + self.calculate_tfidf(word, doc_id)

        results = [
            {"doc_id": doc_id, "score": score}
            for doc_id, score in scores.items()
            if score > 0.0
        ]
        results.sort(key=lambda r: r["score"], reverse=True)
        return results

    def rank_documents_and(self, query):
        if query is None:
            raise ValueError("Query cannot be None")
        if not query.strip():
            raise ValueError("Query cannot be empty")

        words = tokenize(query)
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
            score = sum(self.calculate_tfidf(word, doc_id) for word in words)
            if score > 0.0:
                results.append({"doc_id": doc_id, "score": score})

        results.sort(key=lambda r: r["score"], reverse=True)
        return results

    def rank_phrase(self, phrase):
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
        if query is None:
            raise ValueError("Query cannot be None")

        results = []
        for r in self.rank_documents(query)[:limit]:
            results.append({
                "doc_id": r["doc_id"],
                "score": r["score"],
                "snippet": self.indexer.documents.get(r["doc_id"], "")[:100],
            })
        return results
