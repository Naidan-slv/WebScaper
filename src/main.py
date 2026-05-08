"""Command-line entry point for the COMP3011 search engine tool."""

import os

from src.crawler import Crawler, MultiPageCrawler
from src.indexer import Indexer, Persistence, WordFrequency, tokenize
from src.search import MultiwordSearch, Search, TfIdf


DEFAULT_INDEX_DIR = "data"
DEFAULT_INDEX_FILE = os.path.join(DEFAULT_INDEX_DIR, "index.json")
DEFAULT_DOCS_FILE = os.path.join(DEFAULT_INDEX_DIR, "documents.json")
BASE_URL = "https://quotes.toscrape.com"


class CLI:
    """Interactive shell with build, load, print, and find commands."""

    def __init__(self):
        self.crawler = Crawler(timeout=15, politeness_delay=6)
        self.indexer = Indexer()
        self.search = None
        self.multiword_search = None
        self.word_freq = None
        self.tfidf = None
        self.persistence = None
        self.is_built = False

    def build(self, max_pages=10):
        print(f"\nCrawling {BASE_URL} (up to {max_pages} pages)...")
        print("Respecting 6-second politeness window between requests.\n")

        mpc = MultiPageCrawler(self.crawler, max_pages=max_pages, base_url=BASE_URL)
        pages = mpc.fetch_and_parse_all()
        print(f"  Fetched {len(pages)} pages.")

        self.indexer = Indexer()
        for page in pages:
            self.indexer.add_document(page["text"], url=page.get("url"))
        self.indexer.build_index()
        print(f"  Indexed {self.indexer.document_count} documents, {len(self.indexer.index)} unique words.")

        os.makedirs(DEFAULT_INDEX_DIR, exist_ok=True)
        self.persistence = Persistence(self.indexer)
        self.persistence.save_index(DEFAULT_INDEX_FILE)
        self.persistence.save_documents(DEFAULT_DOCS_FILE)
        print(f"  Index saved to {DEFAULT_INDEX_FILE}")
        print(f"  Documents saved to {DEFAULT_DOCS_FILE}")

        self._wire_search_components()

        summary = {
            "pages_crawled": len(pages),
            "words_indexed": len(self.indexer.index),
            "docs_stored": self.indexer.document_count,
        }
        print("\n  Build complete.")
        return summary

    def load(self):
        if not os.path.exists(DEFAULT_INDEX_FILE):
            raise FileNotFoundError(
                f"Index file not found: {DEFAULT_INDEX_FILE}. Run 'build' first."
            )
        if not os.path.exists(DEFAULT_DOCS_FILE):
            raise FileNotFoundError(
                f"Documents file not found: {DEFAULT_DOCS_FILE}. Run 'build' first."
            )

        print(f"\nLoading index from {DEFAULT_INDEX_FILE}...")

        self.indexer = Indexer()
        self.persistence = Persistence(self.indexer)

        loaded_index = self.persistence.load_index(DEFAULT_INDEX_FILE)
        for word, entries in loaded_index.items():
            if isinstance(entries, dict):
                loaded_index[word] = {int(k): v for k, v in entries.items()}
        self.indexer.index = loaded_index

        loaded_docs = self.persistence.load_documents(DEFAULT_DOCS_FILE)
        for k, v in loaded_docs.items():
            doc_id = int(k)
            if isinstance(v, dict):
                self.indexer.documents[doc_id] = v["text"]
                if "url" in v:
                    self.indexer.urls[doc_id] = v["url"]
            else:
                self.indexer.documents[doc_id] = v
        self.indexer.document_count = len(self.indexer.documents)

        self._wire_search_components()

        summary = {
            "words_loaded": len(self.indexer.index),
            "docs_loaded": self.indexer.document_count,
        }
        print(f"  Loaded {summary['words_loaded']} words, {summary['docs_loaded']} documents.")
        print("  Ready to search.\n")
        return summary

    def print_index(self, word):
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
        if not self.is_built:
            print("No index loaded. Run 'build' or 'load' first.")
            return []

        if query is None:
            print("  Usage: find <query>")
            return []

        query_text = query.strip()
        is_phrase = (
            len(query_text) >= 2
            and query_text[0] == query_text[-1]
            and query_text[0] in ('"', "'")
        )

        if is_phrase:
            query_text = query_text[1:-1].strip()
            if not query_text:
                print("  Usage: find \"<phrase>\"")
                return []
            ranked = self.tfidf.rank_phrase(query_text)
        else:
            ranked = self.tfidf.rank_documents_and(query_text)

        results = []
        for r in ranked:
            doc_id = r["doc_id"]
            url = self.indexer.get_document_url(doc_id)
            words = tokenize(query_text)
            snippet = ""
            if is_phrase and r.get("positions"):
                snippet = self._get_phrase_snippet(doc_id, words, r["positions"][0])
            else:
                for word in words:
                    try:
                        snippet = self.search.get_snippet(doc_id, word, context_words=5)
                        break
                    except (ValueError, RuntimeError):
                        continue
            if not snippet:
                snippet = self.indexer.documents.get(doc_id, "")[:100]

            result = {
                "doc_id": doc_id,
                "score": r["score"],
                "snippet": snippet,
                "url": url,
                "match_type": "phrase" if is_phrase else "terms",
            }
            if is_phrase:
                result["phrase_positions"] = r["positions"]
                result["phrase_frequency"] = r["phrase_frequency"]
            results.append(result)

        if results:
            label = "exact phrase" if is_phrase else "query"
            print(f"\nFound {len(results)} result(s) for {label} '{query_text}' (ranked by relevance):")
            for i, r in enumerate(results, 1):
                url_str = f" {r['url']}" if r["url"] else ""
                print(f"  {i}. [score: {r['score']:.4f}]{url_str} Doc {r['doc_id']}: {r['snippet']}...")
        else:
            label = "exact phrase" if is_phrase else "query"
            print(f"\n  No results for {label} '{query_text}'.")
        return results

    def _get_phrase_snippet(self, doc_id, words, start_pos, context_words=5):
        tokens = tokenize(self.indexer.documents.get(doc_id, ""))
        if not tokens:
            return ""

        start = max(0, start_pos - context_words)
        end = min(len(tokens), start_pos + len(words) + context_words)
        snippet_tokens = tokens[start:end]

        if start > 0:
            snippet_tokens.insert(0, "...")
        if end < len(tokens):
            snippet_tokens.append("...")

        return " ".join(snippet_tokens)

    def _wire_search_components(self):
        self.search = Search(self.indexer)
        self.multiword_search = MultiwordSearch(self.search)
        self.word_freq = WordFrequency(self.indexer)
        self.word_freq.calculate_frequencies()
        self.tfidf = TfIdf(self.indexer)
        self.is_built = True

    def run(self):
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
        print("\nAvailable commands:")
        print("  build         - Crawl website and build index")
        print("  load          - Load saved index from file")
        print("  print <word>  - Print inverted index for word")
        print("  find <query>  - Find pages with search terms")
        print("  find \"phrase\" - Find exact phrase using word positions")
        print("  help          - Show this help message")
        print("  quit / exit   - Exit the program\n")


def main():
    """Launch the search engine CLI."""
    cli = CLI()
    cli.run()


if __name__ == "__main__":
    main()
