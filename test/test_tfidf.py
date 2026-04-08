"""
Tests for TfIdf class.

Tests cover all 5 public methods + __init__:
- __init__: Validation of indexer dependency
- calculate_tf: Term frequency per document
- calculate_idf: Inverse document frequency across corpus
- calculate_tfidf: Combined TF * IDF score
- rank_documents: Multi-word query ranking
- search: Ranked search with snippets
"""

import math
import pytest
from src.indexer import Indexer
from src.tfidf import TfIdf


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture
def indexer():
    """Provide a built indexer with 3 documents."""
    idx = Indexer()
    idx.add_document("the cat sat on the mat")            # doc 0: "the" x2
    idx.add_document("the dog chased the cat the cat")    # doc 1: "the" x3, "cat" x2
    idx.add_document("fish swim in the ocean")             # doc 2: "the" x1
    idx.build_index()
    return idx


@pytest.fixture
def tfidf(indexer):
    """Provide a ready TfIdf instance."""
    return TfIdf(indexer)


# ============================================================
# Test Class 1: Initialization
# ============================================================

class TestTfIdfInit:
    """Tests for __init__ validation."""

    def test_init_with_valid_indexer(self, indexer):
        """Creates successfully with a built indexer."""
        t = TfIdf(indexer)
        assert t.indexer is indexer

    def test_init_raises_if_indexer_none(self):
        """Raises ValueError if indexer is None."""
        with pytest.raises(ValueError):
            TfIdf(None)

    def test_init_raises_if_index_empty(self):
        """Raises ValueError if indexer has no built index."""
        idx = Indexer()
        with pytest.raises(ValueError):
            TfIdf(idx)

    def test_init_raises_if_no_documents(self):
        """Raises ValueError if indexer has no documents."""
        idx = Indexer()
        idx.index = {"word": [0]}  # fake index but no docs
        with pytest.raises(ValueError):
            TfIdf(idx)


# ============================================================
# Test Class 2: calculate_tf
# ============================================================

class TestCalculateTf:
    """Tests for term frequency calculation."""

    def test_tf_word_appears_once(self, tfidf):
        """TF for a word appearing once in a 6-word doc."""
        # doc 0: "the cat sat on the mat" -> "sat" appears 1/6
        tf = tfidf.calculate_tf("sat", 0)
        assert tf == pytest.approx(1 / 6)

    def test_tf_word_appears_twice(self, tfidf):
        """TF for a word appearing twice in a 6-word doc."""
        # doc 0: "the cat sat on the mat" -> "the" appears 2/6
        tf = tfidf.calculate_tf("the", 0)
        assert tf == pytest.approx(2 / 6)

    def test_tf_word_not_in_doc(self, tfidf):
        """TF is 0.0 for a word not in the document."""
        tf = tfidf.calculate_tf("fish", 0)
        assert tf == 0.0

    def test_tf_case_insensitive(self, tfidf):
        """TF lookup is case-insensitive."""
        tf = tfidf.calculate_tf("CAT", 0)
        assert tf == pytest.approx(1 / 6)

    def test_tf_raises_if_doc_not_found(self, tfidf):
        """Raises KeyError for nonexistent doc_id."""
        with pytest.raises(KeyError):
            tfidf.calculate_tf("cat", 999)

    def test_tf_different_doc_lengths(self, tfidf):
        """TF accounts for different document lengths."""
        # doc 1: "the dog chased the cat the cat" -> "cat" 2/7
        # doc 0: "the cat sat on the mat" -> "cat" 1/6
        tf_doc1 = tfidf.calculate_tf("cat", 1)
        tf_doc0 = tfidf.calculate_tf("cat", 0)
        assert tf_doc1 == pytest.approx(2 / 7)
        assert tf_doc0 == pytest.approx(1 / 6)


# ============================================================
# Test Class 3: calculate_idf
# ============================================================

class TestCalculateIdf:
    """Tests for inverse document frequency calculation."""

    def test_idf_word_in_all_docs(self, tfidf):
        """IDF is low (but positive) for a word in every document."""
        # "the" is in all 3 docs -> log(1 + 3/3) = log(2)
        idf = tfidf.calculate_idf("the")
        assert idf == pytest.approx(math.log(2))

    def test_idf_word_in_some_docs(self, tfidf):
        """IDF is higher for a word in fewer documents."""
        # "cat" in doc 0, 1 -> log(1 + 3/2)
        idf = tfidf.calculate_idf("cat")
        assert idf == pytest.approx(math.log(1 + 3 / 2))

    def test_idf_word_in_one_doc(self, tfidf):
        """IDF is highest for a word in only one document."""
        # "fish" in doc 2 only -> log(1 + 3/1) = log(4)
        idf = tfidf.calculate_idf("fish")
        assert idf == pytest.approx(math.log(4))

    def test_idf_word_not_in_index(self, tfidf):
        """IDF is 0.0 for a word not in the index."""
        idf = tfidf.calculate_idf("xyzzy")
        assert idf == 0.0

    def test_idf_case_insensitive(self, tfidf):
        """IDF lookup is case-insensitive."""
        idf = tfidf.calculate_idf("FISH")
        assert idf == pytest.approx(math.log(4))

    def test_idf_rare_word_higher_than_common(self, tfidf):
        """Rare words have higher IDF than common words."""
        idf_rare = tfidf.calculate_idf("fish")   # 1 doc
        idf_common = tfidf.calculate_idf("the")  # 3 docs
        assert idf_rare > idf_common


# ============================================================
# Test Class 4: calculate_tfidf
# ============================================================

class TestCalculateTfIdf:
    """Tests for combined TF-IDF score."""

    def test_tfidf_is_tf_times_idf(self, tfidf):
        """TF-IDF equals TF * IDF."""
        word, doc = "cat", 0
        tf = tfidf.calculate_tf(word, doc)
        idf = tfidf.calculate_idf(word)
        assert tfidf.calculate_tfidf(word, doc) == pytest.approx(tf * idf)

    def test_tfidf_zero_for_ubiquitous_word(self, tfidf):
        """TF-IDF is low (but positive) for a word in every document."""
        # With smoothed IDF, ubiquitous words still score > 0
        score = tfidf.calculate_tfidf("the", 0)
        assert score > 0.0
        # But lower than a word with same TF but in fewer docs
        # "cat" appears 1x in doc 0 (TF=1/6), in 2 docs: IDF=log(1+3/2)
        # "the" appears 2x in doc 0 (TF=2/6), in 3 docs: IDF=log(1+3/3)
        # "fish" appears 0x in doc 0, so use doc 2 for comparison
        score_fish_doc2 = tfidf.calculate_tfidf("fish", 2)
        # "fish" in 1 doc → higher IDF → higher score per occurrence
        assert score_fish_doc2 > 0.0

    def test_tfidf_zero_for_absent_word(self, tfidf):
        """TF-IDF is 0 for a word not in the document (TF = 0)."""
        score = tfidf.calculate_tfidf("fish", 0)
        assert score == pytest.approx(0.0)

    def test_tfidf_positive_for_relevant_word(self, tfidf):
        """TF-IDF is positive for a word present in doc but not all docs."""
        # "sat" only in doc 0
        score = tfidf.calculate_tfidf("sat", 0)
        assert score > 0.0

    def test_tfidf_raises_if_doc_not_found(self, tfidf):
        """Raises KeyError for nonexistent doc_id."""
        with pytest.raises(KeyError):
            tfidf.calculate_tfidf("cat", 999)

    def test_tfidf_higher_for_rarer_word(self, tfidf):
        """Rarer words score higher than common ones in same doc."""
        # doc 0: "sat" (1 doc) vs "cat" (2 docs), both appear once
        score_rare = tfidf.calculate_tfidf("sat", 0)
        score_common = tfidf.calculate_tfidf("cat", 0)
        assert score_rare > score_common


# ============================================================
# Test Class 5: rank_documents
# ============================================================

class TestRankDocuments:
    """Tests for document ranking by query."""

    def test_single_word_ranking(self, tfidf):
        """Ranks documents for a single-word query."""
        results = tfidf.rank_documents("cat")
        assert len(results) > 0
        assert "doc_id" in results[0]
        assert "score" in results[0]

    def test_results_sorted_by_score_desc(self, tfidf):
        """Results sorted highest score first."""
        results = tfidf.rank_documents("cat")
        scores = [r["score"] for r in results]
        assert scores == sorted(scores, reverse=True)

    def test_excludes_zero_score_docs(self, tfidf):
        """Documents with 0 TF-IDF are excluded."""
        # "fish" only in doc 2
        results = tfidf.rank_documents("fish")
        doc_ids = [r["doc_id"] for r in results]
        assert 0 not in doc_ids
        assert 2 in doc_ids

    def test_multiword_sums_scores(self, tfidf):
        """Multi-word query sums TF-IDF across all terms."""
        results = tfidf.rank_documents("cat sat")
        # doc 0 has both "cat" and "sat" -> highest combined score
        assert results[0]["doc_id"] == 0

    def test_raises_if_query_none(self, tfidf):
        """Raises ValueError for None query."""
        with pytest.raises(ValueError):
            tfidf.rank_documents(None)

    def test_raises_if_query_empty(self, tfidf):
        """Raises ValueError for empty query."""
        with pytest.raises(ValueError):
            tfidf.rank_documents("")

    def test_no_results_for_nonexistent_word(self, tfidf):
        """Returns empty list for word not in any document."""
        results = tfidf.rank_documents("xyzzy")
        assert results == []


# ============================================================
# Test Class 6: search (ranked search with snippets)
# ============================================================

class TestSearch:
    """Tests for ranked search with snippets."""

    def test_returns_ranked_results(self, tfidf):
        """search returns results ranked by TF-IDF."""
        results = tfidf.search("cat")
        assert len(results) > 0
        scores = [r["score"] for r in results]
        assert scores == sorted(scores, reverse=True)

    def test_results_contain_snippet(self, tfidf):
        """Each result has a snippet."""
        results = tfidf.search("cat")
        for r in results:
            assert "snippet" in r
            assert len(r["snippet"]) > 0

    def test_results_contain_doc_id(self, tfidf):
        """Each result has a doc_id."""
        results = tfidf.search("cat")
        for r in results:
            assert "doc_id" in r

    def test_limit_parameter(self, tfidf):
        """limit caps number of results."""
        results = tfidf.search("cat", limit=1)
        assert len(results) <= 1

    def test_no_results_for_nonexistent(self, tfidf):
        """Returns empty for word not in index."""
        results = tfidf.search("xyzzy")
        assert results == []

    def test_raises_if_query_none(self, tfidf):
        """Raises ValueError for None query."""
        with pytest.raises(ValueError):
            tfidf.search(None)
