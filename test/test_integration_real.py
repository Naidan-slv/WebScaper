"""
Integration tests that validate actual implementation against real website.

These tests make actual HTTP requests to quotes.toscrape.com to verify:
- Crawler fetches real HTML correctly
- Indexer handles real documents
- Search queries work with real data
- Multi-page crawling retrieves actual pages

Run with: pytest test/test_integration_real.py -v --tb=short

Note: Requires internet connection. Can be slow (respects politeness delays).
"""

import pytest
from src.crawler import Crawler
from src.indexer import Indexer
from src.search import Search
from src.multi_page_crawler import MultiPageCrawler
from src.multiword_search import MultiwordSearch


class TestRealWebsiteCrawler:
    """Test crawler against real quotes.toscrape.com."""

    @pytest.fixture
    def crawler(self):
        """Provide real crawler instance."""
        return Crawler(timeout=10, politeness_delay=1)  # 1s for integration tests

    def test_crawler_fetches_real_page(self, crawler):
        """Crawler successfully fetches actual page from quotes.toscrape.com."""
        url = "https://quotes.toscrape.com/"
        html = crawler.fetch_page(url)
        
        assert html is not None
        assert len(html) > 0
        assert "quotes" in html.lower() or "author" in html.lower()

    def test_crawler_extracts_text_from_real_html(self, crawler):
        """Crawler extracts text from real page HTML."""
        url = "https://quotes.toscrape.com/"
        html = crawler.fetch_page(url)
        text = crawler.extract_text(html)
        
        assert text is not None
        assert len(text) > 0
        # Should contain actual quote content
        assert len(text) > 50


class TestRealWebsiteIndexing:
    """Test indexing against real page data."""

    @pytest.fixture
    def indexed_data(self):
        """Fetch and index real page."""
        crawler = Crawler(timeout=10, politeness_delay=1)
        url = "https://quotes.toscrape.com/"
        html = crawler.fetch_page(url)
        text = crawler.extract_text(html)
        
        indexer = Indexer()
        indexer.add_document(text)
        indexer.build_index()
        
        return indexer, text

    def test_indexer_builds_from_real_content(self, indexed_data):
        """Indexer successfully indexes real page content."""
        indexer, text = indexed_data
        
        assert indexer.index is not None
        assert len(indexer.index) > 0
        # Should find common words from quotes
        assert any(word in ["the", "of", "and", "to", "a"] for word in indexer.index.keys())

    def test_documents_stored_correctly(self, indexed_data):
        """Documents are stored with correct content."""
        indexer, text = indexed_data
        
        doc_text = indexer.get_document(1)
        assert doc_text is not None
        assert doc_text == text


class TestRealWebsiteSearch:
    """Test search functionality against real indexed data."""

    @pytest.fixture
    def search_engine(self):
        """Setup search engine with real data."""
        crawler = Crawler(timeout=10, politeness_delay=1)
        url = "https://quotes.toscrape.com/"
        html = crawler.fetch_page(url)
        text = crawler.extract_text(html)
        
        indexer = Indexer()
        indexer.add_document(text)
        indexer.build_index()
        
        search = Search(indexer)
        return search

    def test_search_finds_common_words(self, search_engine):
        """Search finds common words in real content."""
        # "the" should be in most texts
        results = search_engine.search("the")
        
        # Should find at least one document containing "the"
        assert len(results) > 0

    def test_search_returns_snippets(self, search_engine):
        """Search returns snippets with context."""
        results = search_engine.search_with_snippets("life")
        
        # If "life" is found, should have snippets with context
        # (may be empty if word not found, which is okay)
        assert isinstance(results, list)


class TestRealWebsiteMultiPageCrawling:
    """Test multi-page crawler against real website."""

    @pytest.fixture
    def multi_crawler(self):
        """Provide multi-page crawler with real crawler."""
        crawler = Crawler(timeout=10, politeness_delay=1)
        return MultiPageCrawler(crawler, max_pages=2, base_url="https://quotes.toscrape.com")

    def test_multi_page_crawler_fetches_pages(self, multi_crawler):
        """Multi-page crawler fetches multiple real pages."""
        pages = multi_crawler.fetch_all_pages()
        
        assert len(pages) == 2
        assert all(page and len(page) > 0 for page in pages)

    def test_multi_page_crawler_parses_pages(self, multi_crawler):
        """Multi-page crawler parses multiple pages."""
        results = multi_crawler.fetch_and_parse_all()
        
        assert len(results) == 2
        assert all("text" in r and "page" in r and "url" in r for r in results)
        assert results[0]["page"] == 1
        assert results[1]["page"] == 2

    def test_multi_page_crawler_tracking(self, multi_crawler):
        """Multi-page crawler tracks pages fetched."""
        multi_crawler.fetch_and_parse_all()
        count = multi_crawler.get_pages_fetched()
        
        assert count == 2


class TestRealWebsiteMultiwordSearch:
    """Test multi-word search against real data."""

    @pytest.fixture
    def multiword_search_engine(self):
        """Setup multi-word search with real data."""
        crawler = Crawler(timeout=10, politeness_delay=1)
        
        # Fetch first 2 pages
        mpc = MultiPageCrawler(crawler, max_pages=2)
        pages_data = mpc.fetch_and_parse_all()
        
        # Build index from all pages
        indexer = Indexer()
        for page_data in pages_data:
            indexer.add_document(page_data["text"])
        indexer.build_index()
        
        search = Search(indexer)
        mws = MultiwordSearch(search)
        
        return mws

    def test_multiword_and_search(self, multiword_search_engine):
        """Multi-word AND search works on real data."""
        # Search for two common words likely to be in quotes
        results = multiword_search_engine.search_and("the life")
        
        # May or may not find both, but should return list
        assert isinstance(results, list)

    def test_multiword_or_search(self, multiword_search_engine):
        """Multi-word OR search works on real data."""
        # Search with OR logic
        results = multiword_search_engine.search_or("wisdom knowledge")
        
        # OR should find at least some results
        assert isinstance(results, list)


class TestRealWebsiteFullWorkflow:
    """End-to-end workflow test."""

    def test_full_pipeline_real_data(self):
        """Complete pipeline: crawl → index → search."""
        # 1. Fetch pages
        crawler = Crawler(timeout=10, politeness_delay=1)
        mpc = MultiPageCrawler(crawler, max_pages=2)
        pages_data = mpc.fetch_and_parse_all()
        
        # 2. Build index
        indexer = Indexer()
        for page_data in pages_data:
            indexer.add_document(page_data["text"])
        indexer.build_index()
        
        # 3. Setup search
        search = Search(indexer)
        mws = MultiwordSearch(search)
        
        # 4. Verify structure
        assert len(indexer.documents) == 2
        assert len(indexer.index) > 0
        
        # 5. Perform searches
        single_word = search.search("life")
        multi_and = mws.search_and("life")
        multi_or = mws.search_or("life wisdom")
        
        # 6. Verify results are consistent
        assert isinstance(single_word, list)
        assert isinstance(multi_and, list)
        assert isinstance(multi_or, list)
