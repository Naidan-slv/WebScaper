"""
Command-line interface for the Search Engine Tool.

Implements the 4 required commands from the COMP3011 coursework brief:
  > build   - Crawl website, build index, save to file
  > load    - Load previously saved index from file
  > print   - Print inverted index for a word
  > find    - Find pages containing search terms
"""

import os
from src.crawler import Crawler
from src.indexer import Indexer
from src.search import Search
from src.multi_page_crawler import MultiPageCrawler
from src.multiword_search import MultiwordSearch
from src.word_frequency import WordFrequency
from src.persistence import Persistence
from src.tfidf import TfIdf


# Default paths for index storage
DEFAULT_INDEX_DIR = "data"
DEFAULT_INDEX_FILE = os.path.join(DEFAULT_INDEX_DIR, "index.json")
DEFAULT_DOCS_FILE = os.path.join(DEFAULT_INDEX_DIR, "documents.json")
BASE_URL = "https://quotes.toscrape.com"


class CLI:
    """Command-line interface for the search engine tool."""

    def __init__(self):
        """Initialize CLI with no components loaded yet."""
        self.crawler = Crawler(timeout=15, politeness_delay=6)
        self.indexer = Indexer()
        self.search = None
        self.multiword_search = None
        self.word_freq = None
        self.tfidf = None
        self.persistence = None
        self.is_built = False

    def build(self, max_pages=10):
        """
        Crawl the website, build the index, and save to file system.

        Implements: > build

        Args:
            max_pages: Maximum number of pages to crawl (default 10)

        Returns:
            dict: Summary with pages_crawled, words_indexed, docs_stored
        """
        print(f"\nCrawling {BASE_URL} (up to {max_pages} pages)...")
        print("Respecting 6-second politeness window between requests.\n")

        # 1. Crawl all pages
        mpc = MultiPageCrawler(self.crawler, max_pages=max_pages, base_url=BASE_URL)
        pages = mpc.fetch_and_parse_all()
        print(f"  Fetched {len(pages)} pages.")

        # 2. Index all pages
        self.indexer = Indexer()  # Fresh indexer
        for page in pages:
            self.indexer.add_document(page["text"], url=page.get("url"))
        self.indexer.build_index()
        print(f"  Indexed {self.indexer.document_count} documents, {len(self.indexer.index)} unique words.")

        # 3. Save to file system
        os.makedirs(DEFAULT_INDEX_DIR, exist_ok=True)
        self.persistence = Persistence(self.indexer)
        self.persistence.save_index(DEFAULT_INDEX_FILE)
        self.persistence.save_documents(DEFAULT_DOCS_FILE)
        print(f"  Index saved to {DEFAULT_INDEX_FILE}")
        print(f"  Documents saved to {DEFAULT_DOCS_FILE}")

        # 4. Wire up search components
        self._wire_search_components()

        summary = {
            "pages_crawled": len(pages),
            "words_indexed": len(self.indexer.index),
            "docs_stored": self.indexer.document_count,
        }
        print(f"\n  Build complete.")
        return summary

    def load(self):
        """
        Load a previously saved index from the file system.

        Implements: > load

        Returns:
            dict: Summary with words_loaded, docs_loaded

        Raises:
            FileNotFoundError: If index files don't exist
        """
        if not os.path.exists(DEFAULT_INDEX_FILE):
            raise FileNotFoundError(
                f"Index file not found: {DEFAULT_INDEX_FILE}. Run 'build' first."
            )
        if not os.path.exists(DEFAULT_DOCS_FILE):
            raise FileNotFoundError(
                f"Documents file not found: {DEFAULT_DOCS_FILE}. Run 'build' first."
            )

        print(f"\nLoading index from {DEFAULT_INDEX_FILE}...")

        # Load index
        self.indexer = Indexer()
        self.persistence = Persistence(self.indexer)

        loaded_index = self.persistence.load_index(DEFAULT_INDEX_FILE)
        # Convert string doc_id keys to int in the rich index structure
        for word, entries in loaded_index.items():
            if isinstance(entries, dict):
                loaded_index[word] = {int(k): v for k, v in entries.items()}
        self.indexer.index = loaded_index

        loaded_docs = self.persistence.load_documents(DEFAULT_DOCS_FILE)
        # Convert string keys back to int keys, handle both old and new format
        for k, v in loaded_docs.items():
            doc_id = int(k)
            if isinstance(v, dict):
                # New format: {"text": str, "url": str}
                self.indexer.documents[doc_id] = v["text"]
                if "url" in v:
                    self.indexer.urls[doc_id] = v["url"]
            else:
                # Old format: just text
                self.indexer.documents[doc_id] = v
        self.indexer.document_count = len(self.indexer.documents)

        # Wire up search
        self._wire_search_components()

        summary = {
            "words_loaded": len(self.indexer.index),
            "docs_loaded": self.indexer.document_count,
        }
        print(f"  Loaded {summary['words_loaded']} words, {summary['docs_loaded']} documents.")
        print("  Ready to search.\n")
        return summary

    def print_index(self, word):
        """
        Print the inverted index entry for a given word with statistics.

        Implements: > print <word>

        Args:
            word: The word to look up in the index

        Returns:
            dict or None: {word, doc_ids, entries} with frequency/positions, or None
        """
        if not self.is_built:
            print("No index loaded. Run 'build' or 'load' first.")
            return None

        entry = self.indexer.get_index_entry(word)
        if entry is not None:
            word_lower = word.lower()
            doc_ids = sorted(entry.keys())
            entries = []
            print(f"\nIndex entry for '{word_lower}':")
            for doc_id in doc_ids:
                stats = entry[doc_id]
                freq = stats["frequency"]
                positions = stats["positions"]
                url = self.indexer.get_document_url(doc_id)
                entries.append({"doc_id": doc_id, "frequency": freq, "positions": positions, "url": url})
                url_str = f" ({url})" if url else ""
                print(f"  Doc {doc_id}{url_str}: frequency={freq}, positions={positions}")
            return {"word": word_lower, "doc_ids": doc_ids, "entries": entries}

        print(f"\n  '{word.lower()}' not found in index.")
        return None

    def find(self, query):
        """
        Find pages containing ALL given search terms (AND logic), ranked by TF-IDF.

        Implements: > find <query>

        Args:
            query: Search query (single or multiple words)

        Returns:
            list: Search results ranked by TF-IDF score, each with
                  doc_id, score, and snippet.
        """
        if not self.is_built:
            print("No index loaded. Run 'build' or 'load' first.")
            return []

        ranked = self.tfidf.rank_documents_and(query)
        results = []
        for r in ranked:
            doc_id = r["doc_id"]
            url = self.indexer.get_document_url(doc_id)
            # Generate context-aware snippet around the first matching query word
            words = query.lower().split()
            snippet = ""
            for word in words:
                try:
                    snippet = self.search.get_snippet(doc_id, word, context_words=5)
                    break
                except (ValueError, RuntimeError):
                    continue
            if not snippet:
                snippet = self.indexer.documents.get(doc_id, "")[:100]
            results.append({
                "doc_id": doc_id,
                "score": r["score"],
                "snippet": snippet,
                "url": url,
            })

        if results:
            print(f"\nFound {len(results)} result(s) for '{query}' (ranked by relevance):")
            for i, r in enumerate(results, 1):
                url_str = f" {r['url']}" if r["url"] else ""
                print(f"  {i}. [score: {r['score']:.4f}]{url_str} Doc {r['doc_id']}: {r['snippet']}...")
        else:
            print(f"\n  No results for '{query}'.")
        return results

    def _wire_search_components(self):
        """Set up search, multiword search, word frequency, and TF-IDF after indexing."""
        self.search = Search(self.indexer)
        self.multiword_search = MultiwordSearch(self.search)
        self.word_freq = WordFrequency(self.indexer)
        self.word_freq.calculate_frequencies()
        self.tfidf = TfIdf(self.indexer)
        self.is_built = True

    def run(self):
        """
        Run the interactive command-line shell.

        Commands:
            build       - Crawl website and build index
            load        - Load saved index from file
            print <w>   - Print inverted index for word
            find <q>    - Find pages with search terms
            help        - Show available commands
            quit/exit   - Exit the program
        """
        print("\nSearch Engine Tool — COMP3011 Coursework")
        print("Type 'help' for available commands.\n")

        try:
            while True:
                user_input = input("> ").strip()
                if not user_input:
                    continue

                parts = user_input.split(maxsplit=1)
                command = parts[0].lower()
                args = parts[1] if len(parts) > 1 else ""

                if command in ("quit", "exit"):
                    print("Goodbye!")
                    break
                elif command == "help":
                    self._print_help()
                elif command == "build":
                    self.build()
                elif command == "load":
                    try:
                        self.load()
                    except FileNotFoundError as e:
                        print(f"  Error: {e}")
                elif command == "print":
                    if not args:
                        print("  Usage: print <word>")
                    else:
                        self.print_index(args)
                elif command == "find":
                    if not args:
                        print("  Usage: find <query>")
                    else:
                        self.find(args)
                else:
                    print(f"  Unknown command: '{command}'. Type 'help' for options.")

        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")

    def _print_help(self):
        """Print available commands."""
        print("\nAvailable commands:")
        print("  build         - Crawl website and build index")
        print("  load          - Load saved index from file")
        print("  print <word>  - Print inverted index for word")
        print("  find <query>  - Find pages with search terms")
        print("  help          - Show this help message")
        print("  quit / exit   - Exit the program\n")
