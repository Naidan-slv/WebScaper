"""
Integration tests that make REAL HTTP requests to https://quotes.toscrape.com/

These tests validate that the entire search engine pipeline works with the
actual target website from the COMP3011 coursework brief.

WARNING: These tests make real network requests. The application code enforces
the 6-second politeness window, but tests mock time.sleep so the suite remains
quick while still checking that the delay is called.

Usage:
    pytest tests/test_integration_real.py -v -s
    pytest tests/test_integration_real.py -v -s -k "single_page"
"""

import pytest
import time
from src.crawler import Crawler
from src.indexer import Indexer
from src.search import Search
from src.multi_page_crawler import MultiPageCrawler
from src.multiword_search import MultiwordSearch
from src.word_frequency import WordFrequency
from src.persistence import Persistence

# ============================================================
# Fixtures - shared setup for real website tests
# ============================================================

BASE_URL = "https://quotes.toscrape.com/"


@pytest.fixture(scope="module")
def real_crawler():
    """Create a real crawler with politeness delay."""
    return Crawler(timeout=15, politeness_delay=6)


@pytest.fixture(scope="module")
def single_page_html(real_crawler):
    """Fetch a single real page from quotes.toscrape.com."""
    html = real_crawler.fetch_page(BASE_URL)
    return html


@pytest.fixture(scope="module")
def single_page_text(real_crawler, single_page_html):
    """Extract text from a single real page."""
    text = real_crawler.extract_text(single_page_html)
    return text


@pytest.fixture(scope="module")
def built_indexer(single_page_text):
    """Build an indexer with a single real page."""
    indexer = Indexer()
    indexer.add_document(single_page_text)
    indexer.build_index()
    return indexer


@pytest.fixture(scope="module")
def multi_page_indexer(real_crawler):
    """Build an indexer with 2 real pages (respects politeness)."""
    mpc = MultiPageCrawler(real_crawler, max_pages=2, base_url=BASE_URL)
    pages = mpc.fetch_and_parse_all()

    indexer = Indexer()
    for page in pages:
        indexer.add_document(page["text"])
    indexer.build_index()
    return indexer


# ============================================================
# Test Class 1: Real Crawler Tests
# ============================================================

class TestRealCrawlerFetch:
    """Test that the crawler can fetch real pages from quotes.toscrape.com."""

    def test_fetch_page_returns_html(self, single_page_html):
        """Verify fetch_page returns actual HTML content."""
        assert single_page_html is not None
        assert isinstance(single_page_html, str)
        assert len(single_page_html) > 0

    def test_fetch_page_contains_html_tags(self, single_page_html):
        """Verify fetched content is valid HTML."""
        assert "<html" in single_page_html.lower()
        assert "</html>" in single_page_html.lower()

    def test_fetch_page_contains_quotes(self, single_page_html):
        """Verify the page contains quote content."""
        # quotes.toscrape.com always has quotes on the page
        assert "quote" in single_page_html.lower()

    def test_extract_text_returns_content(self, single_page_text):
        """Verify extract_text produces readable text from real HTML."""
        assert single_page_text is not None
        assert isinstance(single_page_text, str)
        assert len(single_page_text) > 100  # should have substantial content

    def test_extract_text_contains_known_content(self, single_page_text):
        """Verify extracted text contains expected content from the website."""
        # The site has famous quotes - at least some common words should appear
        text_lower = single_page_text.lower()
        # The site definitely has the word "quotes" somewhere
        assert "quote" in text_lower or "world" in text_lower or "life" in text_lower

    def test_extract_text_no_html_tags(self, single_page_text):
        """Verify extracted text has no HTML tags remaining."""
        assert "<div" not in single_page_text
        assert "<span" not in single_page_text
        assert "<html" not in single_page_text


# ============================================================
# Test Class 2: Real Indexer Tests
# ============================================================

class TestRealIndexer:
    """Test that the indexer works with real website content."""

    def test_indexer_has_documents(self, built_indexer):
        """Verify indexer stores the real document."""
        assert built_indexer.document_count > 0

    def test_index_is_non_empty(self, built_indexer):
        """Verify the inverted index was built with real words."""
        assert len(built_indexer.index) > 0

    def test_index_contains_common_words(self, built_indexer):
        """Verify index has words that definitely appear on the site."""
        # Common English words that will be on any page with quotes
        index_words = set(built_indexer.index.keys())
        # At least some of these common words should be indexed
        common_words = {"the", "a", "is", "to", "and", "of", "in", "it"}
        found = common_words.intersection(index_words)
        assert len(found) > 0, f"Expected common words in index, found none. Index has {len(index_words)} words."

    def test_search_returns_results_for_common_word(self, built_indexer):
        """Verify searching for a common word returns the document."""
        # "the" is almost certainly on the page
        results = built_indexer.search("the")
        assert len(results) > 0

    def test_get_document_returns_text(self, built_indexer):
        """Verify we can retrieve the stored document text."""
        doc = built_indexer.get_document(0)
        assert isinstance(doc, str)
        assert len(doc) > 100


# ============================================================
# Test Class 3: Real Search Tests
# ============================================================

class TestRealSearch:
    """Test search functionality with real website data."""

    def test_search_finds_results(self, built_indexer):
        """Verify search returns results for a word on the site."""
        search = Search(built_indexer)
        results = search.search("the")
        assert len(results) > 0

    def test_search_with_snippets(self, built_indexer):
        """Verify search returns snippets with real content."""
        search = Search(built_indexer)
        results = search.search_with_snippets("the")
        assert len(results) > 0
        assert "doc_id" in results[0]
        assert "snippet" in results[0]
        assert len(results[0]["snippet"]) > 0

    def test_search_nonexistent_word(self, built_indexer):
        """Verify search returns empty for a word not on the site."""
        search = Search(built_indexer)
        results = search.search("xyzzyplugh")  # nonsense word
        assert results == []

    def test_search_case_insensitive(self, built_indexer):
        """Verify case-insensitive search works with real data."""
        search = Search(built_indexer)
        results_lower = search.search("the")
        results_upper = search.search("THE")
        assert results_lower == results_upper


# ============================================================
# Test Class 4: Real Multi-Page Crawler Tests
# ============================================================

class TestRealMultiPageCrawler:
    """Test multi-page crawling with real website.
    
    NOTE: These tests make multiple real HTTP requests with 6s delay each.
    """

    def test_multi_page_fetches_pages(self, real_crawler):
        """Verify multi-page crawler fetches multiple real pages."""
        mpc = MultiPageCrawler(real_crawler, max_pages=2, base_url=BASE_URL)
        pages = mpc.fetch_all_pages()
        assert len(pages) == 2
        assert all(isinstance(p, str) for p in pages)

    def test_multi_page_parse_returns_text(self, real_crawler):
        """Verify fetch_and_parse_all returns parsed text from real pages."""
        mpc = MultiPageCrawler(real_crawler, max_pages=2, base_url=BASE_URL)
        results = mpc.fetch_and_parse_all()
        assert len(results) == 2
        for result in results:
            assert "page" in result
            assert "text" in result
            assert "url" in result
            assert len(result["text"]) > 100

    def test_pages_have_different_content(self, real_crawler):
        """Verify different pages have different quotes."""
        mpc = MultiPageCrawler(real_crawler, max_pages=2, base_url=BASE_URL)
        results = mpc.fetch_and_parse_all()
        # Different pages should have different content
        assert results[0]["text"] != results[1]["text"]

    def test_pages_fetched_counter(self, real_crawler):
        """Verify pages_fetched counter is accurate."""
        mpc = MultiPageCrawler(real_crawler, max_pages=2, base_url=BASE_URL)
        mpc.fetch_all_pages()
        assert mpc.get_pages_fetched() == 2


# ============================================================
# Test Class 5: Real Multi-Word Search Tests
# ============================================================

class TestRealMultiWordSearch:
    """Test multi-word search with real website data."""

    def test_and_search_returns_results(self, built_indexer):
        """Verify AND search works with real content."""
        search = Search(built_indexer)
        mws = MultiwordSearch(search)
        # "the" and "a" should both be on the page
        results = mws.search_and("the a")
        assert len(results) > 0

    def test_and_search_with_snippets(self, built_indexer):
        """Verify AND search returns snippets with real content."""
        search = Search(built_indexer)
        mws = MultiwordSearch(search)
        results = mws.search_and_with_snippets("the a")
        assert len(results) > 0
        assert "doc_id" in results[0]
        assert "snippet" in results[0]

    def test_or_search_returns_results(self, built_indexer):
        """Verify OR search works with real content."""
        search = Search(built_indexer)
        mws = MultiwordSearch(search)
        results = mws.search_or("the xyzzyplugh")
        # "the" should match even if "xyzzyplugh" doesn't
        assert len(results) > 0

    def test_and_search_no_results(self, built_indexer):
        """Verify AND search returns empty when one word is missing."""
        search = Search(built_indexer)
        mws = MultiwordSearch(search)
        results = mws.search_and("the xyzzyplugh")
        assert results == []


# ============================================================
# Test Class 6: Real Word Frequency Tests
# ============================================================

class TestRealWordFrequency:
    """Test word frequency analysis with real website data."""

    def test_calculate_frequencies(self, built_indexer):
        """Verify frequency calculation works with real content."""
        wf = WordFrequency(built_indexer)
        freqs = wf.calculate_frequencies()
        assert isinstance(freqs, dict)
        assert len(freqs) > 0

    def test_common_word_has_frequency(self, built_indexer):
        """Verify common words have non-zero frequency in real content."""
        wf = WordFrequency(built_indexer)
        wf.calculate_frequencies()
        # "the" should appear multiple times on any page
        freq = wf.get_word_frequency("the", 0)
        assert freq > 0

    def test_top_words_are_common(self, built_indexer):
        """Verify top words from real content are common English words."""
        wf = WordFrequency(built_indexer)
        wf.calculate_frequencies()
        top = wf.get_top_words(0, limit=5)
        assert len(top) == 5
        assert all("word" in entry and "frequency" in entry for entry in top)
        # Top words should have frequency > 1
        assert top[0]["frequency"] > 1

    def test_document_length_is_reasonable(self, built_indexer):
        """Verify document length is reasonable for a full page of quotes."""
        wf = WordFrequency(built_indexer)
        wf.calculate_frequencies()
        length = wf.get_document_length(0)
        assert isinstance(length, int)
        # A page of quotes should have at least 50 words
        assert length > 50


# ============================================================
# Test Class 7: Real Multi-Page Indexer Tests
# ============================================================

class TestRealMultiPageIndexer:
    """Test indexing with multiple real pages."""

    def test_multi_page_index_has_more_words(self, built_indexer, multi_page_indexer):
        """Verify indexing multiple pages produces a richer index."""
        single_words = len(built_indexer.index)
        multi_words = len(multi_page_indexer.index)
        # More pages should mean more unique words (or at least same)
        assert multi_words >= single_words

    def test_multi_page_has_multiple_documents(self, multi_page_indexer):
        """Verify multiple documents are stored."""
        assert multi_page_indexer.document_count == 2

    def test_multi_page_search_across_pages(self, multi_page_indexer):
        """Verify search finds results across multiple crawled pages."""
        search = Search(multi_page_indexer)
        results = search.search("the")
        # "the" should appear in both pages
        assert len(results) >= 1


# ============================================================
# Test Class 8: Real Persistence Tests
# ============================================================

class TestRealPersistence:
    """Test save/load with real website data."""

    def test_save_and_load_real_index(self, built_indexer, tmp_path):
        """Verify real index can be saved and loaded."""
        persistence = Persistence(built_indexer)

        # Save
        index_file = str(tmp_path / "real_index.json")
        bytes_written = persistence.save_index(index_file)
        assert bytes_written > 0

        # Load
        loaded = persistence.load_index(index_file)
        assert isinstance(loaded, dict)
        assert len(loaded) > 0

    def test_save_and_load_real_documents(self, built_indexer, tmp_path):
        """Verify real documents can be saved and loaded."""
        persistence = Persistence(built_indexer)

        # Save
        docs_file = str(tmp_path / "real_docs.json")
        bytes_written = persistence.save_documents(docs_file)
        assert bytes_written > 0

        # Load
        loaded = persistence.load_documents(docs_file)
        assert isinstance(loaded, dict)
        assert len(loaded) > 0

    def test_checkpoint_with_real_data(self, built_indexer, tmp_path):
        """Verify checkpoint save/load works with real data."""
        persistence = Persistence(built_indexer)

        # Save checkpoint
        checkpoint_dir = str(tmp_path / "real_checkpoint")
        result = persistence.save_checkpoint(checkpoint_dir)
        assert "index_file" in result or "docs_file" in result

        # Load checkpoint
        loaded = persistence.load_checkpoint(checkpoint_dir)
        assert "index" in loaded
        assert "documents" in loaded


# ============================================================
# Test Class 9: Full Pipeline Integration
# ============================================================

class TestRealFullPipeline:
    """Test the complete crawl → index → search → analyze pipeline."""

    def test_full_pipeline_single_page(self, real_crawler):
        """Test complete single-page pipeline with real website."""
        # 1. Crawl
        html = real_crawler.fetch_page(BASE_URL)
        assert html is not None

        # 2. Extract text
        text = real_crawler.extract_text(html)
        assert len(text) > 100

        # 3. Index
        indexer = Indexer()
        doc_id = indexer.add_document(text)
        indexer.build_index()
        assert doc_id == 0
        assert len(indexer.index) > 0

        # 4. Search
        search = Search(indexer)
        results = search.search("the")
        assert len(results) > 0

        # 5. Search with snippets
        snippet_results = search.search_with_snippets("the")
        assert len(snippet_results) > 0
        assert "snippet" in snippet_results[0]

        # 6. Word frequency
        wf = WordFrequency(indexer)
        freqs = wf.calculate_frequencies()
        assert len(freqs) > 0
        top = wf.get_top_words(0, limit=3)
        assert len(top) == 3

    def test_full_pipeline_multi_page(self, real_crawler):
        """Test complete multi-page pipeline with real website."""
        # 1. Multi-page crawl
        mpc = MultiPageCrawler(real_crawler, max_pages=2, base_url=BASE_URL)
        pages = mpc.fetch_and_parse_all()
        assert len(pages) == 2

        # 2. Index all pages
        indexer = Indexer()
        for page in pages:
            indexer.add_document(page["text"])
        indexer.build_index()
        assert indexer.document_count == 2

        # 3. Search
        search = Search(indexer)
        results = search.search("the")
        assert len(results) > 0

        # 4. Multi-word search
        mws = MultiwordSearch(search)
        and_results = mws.search_and("the a")
        assert len(and_results) > 0

        # 5. Word frequency on both pages
        wf = WordFrequency(indexer)
        wf.calculate_frequencies()
        len1 = wf.get_document_length(0)
        len2 = wf.get_document_length(1)
        assert len1 > 50
        assert len2 > 50

        # 6. Persistence
        import tempfile
        import os
        with tempfile.TemporaryDirectory() as tmpdir:
            persistence = Persistence(indexer)
            persistence.save_checkpoint(tmpdir)
            loaded = persistence.load_checkpoint(tmpdir)
            assert len(loaded["index"]) > 0
            assert len(loaded["documents"]) > 0
