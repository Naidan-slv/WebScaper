# WebScaper — Search Engine Tool

A search engine tool that crawls [quotes.toscrape.com](https://quotes.toscrape.com/), builds an inverted index of all words across every page, and lets users search for quotes ranked by relevance using TF-IDF. It also supports exact phrase search using word positions stored in the index.

Built for **COMP3011 Web Services and Web Data** (Coursework 2) at the University of Leeds.

## Features

- **Web Crawler** — fetches all pages with a 6-second politeness delay between requests
- **Inverted Index** — maps every word to the documents it appears in, with frequency and position statistics
- **Persistence** — saves/loads generated local JSON files to avoid re-crawling
- **TF-IDF Ranked Search** — single and multi-word queries ranked by relevance using smoothed IDF
- **Exact Phrase Search** — quoted queries use stored word positions to match adjacent words in order
- **Interactive CLI** — four commands: `build`, `load`, `print`, `find`

## Project Structure

```
WebScaper/
├── src/
│   ├── main.py                 # Entry point
│   ├── cli.py                  # Interactive command-line interface
│   ├── crawler.py              # Single-page HTTP fetcher + HTML parser
│   ├── multi_page_crawler.py   # Pagination-aware multi-page crawler
│   ├── indexer.py              # Inverted index builder
│   ├── search.py               # Single-word search
│   ├── multiword_search.py     # Multi-word (AND) search
│   ├── word_frequency.py       # Word frequency statistics
│   ├── tfidf.py                # TF-IDF ranking and phrase search
│   ├── persistence.py          # JSON save/load for generated local files
│   └── utils.py                # Shared utilities
├── tests/
│   ├── conftest.py             # Shared pytest fixtures
│   ├── test_crawler.py         # 16 tests
│   ├── test_multi_page_crawler.py  # 28 tests
│   ├── test_indexer.py         # 21 tests
│   ├── test_search.py          # 29 tests
│   ├── test_multiword_search.py    # 39 tests
│   ├── test_word_frequency.py  # 24 tests
│   ├── test_tfidf.py           # 49 tests
│   ├── test_persistence.py     # 26 tests
│   ├── test_cli.py             # 36 tests
│   ├── test_main.py            # 1 test
│   └── test_integration_real.py    # 35 integration tests (live site)
├── data/
│   └── .gitkeep                # Generated JSON files are ignored by git
├── docs/
│   └── AI_USAGE_LOG.md         # GenAI usage declaration
├── requirements.txt
└── README.md
```

## Installation

**Prerequisites:** Python 3.10+

```bash
# Clone the repository
git clone https://github.com/Naidan-slv/WebScaper.git
cd WebScaper

# Create a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate   # macOS/Linux
# .venv\Scripts\activate    # Windows

# Install dependencies
pip install -r requirements.txt
```

Generated crawl output is not committed to the repository. Running `build` creates `data/index.json` and `data/documents.json` locally; these files are ignored by git because they are derived from the scraped website. The compiled index file can be attached separately for coursework submission.

### Dependencies

| Package | Purpose |
|---|---|
| `requests` | HTTP requests to crawl web pages |
| `beautifulsoup4` | HTML parsing to extract text content |
| `pytest` | Test framework |
| `pytest-cov` | Test coverage reporting |
| `pytest-mock` | Mocking for unit tests |

## Usage

**All commands must be run from the project root directory** (`WebScaper/`):

```bash
cd WebScaper
```

Launch the interactive shell:

```bash
python -m src.main
```

### Commands

#### `build` — Crawl, index, and save

Crawls all pages of quotes.toscrape.com (respecting a 6-second politeness window), builds the inverted index, and saves it to `data/`.

```
> build
Crawling https://quotes.toscrape.com/ (up to 10 pages)...
Respecting 6-second politeness window between requests.

  Fetched 10 pages.
  Indexed 10 documents, 864 unique words.
  Index saved to data/index.json
  Documents saved to data/documents.json

  Build complete.
```

#### `load` — Load a previously saved index

Loads the index from `data/` without re-crawling. Only works after `build` has been run at least once.

```
> load
Loading index from data/index.json...
  Loaded 864 words, 10 documents.
  Ready to search.
```

#### `print <word>` — Show inverted index entry

Displays which documents contain the given word, with frequency and position statistics.

```
> print love
Index entry for 'love':
  Doc 0 (https://quotes.toscrape.com/): frequency=2, positions=[194, 263]
  Doc 1 (https://quotes.toscrape.com/page/2/): frequency=8, positions=[214, 284, 411, 466, 510, 519, 537, 590]
  Doc 2 (https://quotes.toscrape.com/page/3/): frequency=6, positions=[8, 19, 27, 78, 108, 317]

> print xyznotaword
  'xyznotaword' not found in index.
```

#### `find <query>` — Search with TF-IDF ranking

Finds pages matching the query, ranked by TF-IDF relevance score. Multi-word queries use AND logic — only pages containing **all** words are returned.

Quoted queries run exact phrase search. For example, `find good friends` returns pages containing both words anywhere, while `find "good friends"` only returns pages where the words appear next to each other in that order.

```
> find love
Found 10 result(s) for 'love' (ranked by relevance):
  1. [score: 0.0381] https://quotes.toscrape.com/page/5/ Doc 4: ...
  2. [score: 0.0276] https://quotes.toscrape.com/page/2/ Doc 1: ...

> find good friends
Found 6 result(s) for query 'good friends' (ranked by relevance):
  1. [score: 0.0151] https://quotes.toscrape.com/page/2/ Doc 1: ...
  2. [score: 0.0106] https://quotes.toscrape.com/page/6/ Doc 5: ...

> find "good friends"
Found 1 result(s) for exact phrase 'good friends' (ranked by relevance):
  1. [score: 0.0151] https://quotes.toscrape.com/page/2/ Doc 1: ...

> find xyznotaword
  No results for 'xyznotaword'.
```

#### Other commands

```
> help          # Show available commands
> quit          # Exit the program
```

## Testing

The project has **304 tests** across 11 test files: 269 local tests and 35 live integration tests.

**All test commands must be run from the project root directory** (`WebScaper/`).

### Run all unit tests

```bash
python -m pytest --ignore=tests/test_integration_real.py -v
```

### Run all tests including live integration tests

```bash
python -m pytest -v
```

> **Note:** Integration tests (`test_integration_real.py`) make real HTTP requests to quotes.toscrape.com. The application code enforces the 6-second politeness delay during real CLI builds; the test suite mocks `time.sleep` so tests run quickly while still checking that the delay is called.

### Run tests with coverage report

```bash
python -m pytest --ignore=tests/test_integration_real.py --cov=src --cov-report=term-missing
```

### Run a specific test file

```bash
python -m pytest tests/test_tfidf.py -v
```

## Design Decisions

- **Smoothed IDF** — Uses `log(1 + N/df)` instead of the standard `log(N/df)` so that words appearing in every document still receive a small non-zero score. This is essential for small corpora like quotes.toscrape.com (~10 pages) where common words would otherwise score exactly zero.
- **Positional phrase search** — The index stores each word's positions, so quoted queries can verify that words appear consecutively in the correct order.
- **Modular architecture** — Each component (crawler, indexer, search, TF-IDF, persistence) is a separate class with its own test file, following single-responsibility principle.
- **JSON persistence** — The inverted index and document store are serialised locally as JSON for simplicity and human readability, but generated scrape output is ignored by git.
- **Incremental workflow** — Features were developed incrementally with focused tests, semantic commits, and regression checks after each major change.

## GenAI Declaration

This project was developed using **GitHub Copilot** (University of Leeds Secure Copilot Access). Full usage details are documented in [docs/AI_USAGE_LOG.md](docs/AI_USAGE_LOG.md).
