# WebScaper Development Plan: Incremental TDD Approach

## Overview
This document breaks down the project into bite-sized, committable steps. Each step follows TDD: write tests → write minimal code → commit.

**Target**: Show realistic development progression through git history. Each commit should represent a working feature.

---

## Phase 1: Foundation (Days 1-2)

### Step 1: Basic Crawler Setup
**Goal**: Crawl a single page and extract text

**TDD Approach:**
1. Write test: `test_crawler.py::test_fetch_single_page()`
2. Create: `src/crawler.py` with basic `fetch_page()` method
3. Commit: `feat(crawler): implement single page fetching`

**AI Usage Log Entry:**
```
Date: [TODAY]
Task: Basic crawler structure
Used for: [Generate basic fetch_page structure]
Did it help: [Yes/No/Partially]
```

**Files to Create:**
- `test_crawler.py` (test for single page fetch)
- `src/crawler.py` (basic Crawler class)

---

### Step 2: Add Politeness Window
**Goal**: Ensure 6-second delay between requests

**TDD Approach:**
1. Write test: `test_crawler.py::test_politeness_window()`
2. Add: `time.sleep(6)` to crawler
3. Commit: `feat(crawler): implement 6-second politeness window`

**Files Modified:**
- `src/crawler.py` (add time.sleep)
- `tests/test_crawler.py` (add politeness test)

---

### Step 3: Basic Indexer Setup
**Goal**: Create inverted index from page content

**TDD Approach:**
1. Write test: `test_indexer.py::test_build_index_single_page()`
2. Create: `src/indexer.py` with `build_index()` method
3. Commit: `feat(indexer): implement basic inverted index creation`

**Files to Create:**
- `test_indexer.py` (test basic indexing)
- `src/indexer.py` (Indexer class)

---

### Step 4: Basic Search Setup
**Goal**: Find pages by a single word

**TDD Approach:**
1. Write test: `test_search.py::test_find_word_in_index()`
2. Create: `src/search.py` with `find_word()` method
3. Commit: `feat(search): implement single-word search`

**Files to Create:**
- `test_search.py` (test single word search)
- `src/search.py` (Search class)

---

### Step 5: Basic CLI
**Goal**: Simple command-line interface with `build`, `load`, `find`, `print`

**TDD Approach:**
1. Write test: `test_main.py::test_cli_build_command()`
2. Create: `src/main.py` with basic command loop
3. Commit: `feat(main): implement basic CLI interface`

**Files to Create:**
- `src/main.py` (basic CLI)
- `tests/test_main.py` (CLI tests)

**After Phase 1 Git Log Should Look Like:**
```
commit 1a2b3c4 feat(main): implement basic CLI interface
commit 5f6g7h8 feat(search): implement single-word search
commit 9i0j1k2 feat(indexer): implement basic inverted index creation
commit 3l4m5n6 feat(crawler): implement 6-second politeness window
commit 7o8p9q0 feat(crawler): implement single page fetching
```

---

## Phase 2: Core Features (Days 3-5)

### Step 6: Save/Load Index
**Goal**: Persist index to file and load it back

**TDD Approach:**
1. Write test: `test_indexer.py::test_save_and_load_index()`
2. Add methods: `save_index()`, `load_index()` to Indexer
3. Commit: `feat(indexer): implement index persistence`

---

### Step 7: Multi-Word Search
**Goal**: Find pages containing ALL words in query

**TDD Approach:**
1. Write test: `test_search.py::test_find_multiple_words()`
2. Implement: Set intersection logic
3. Commit: `feat(search): implement multi-word search with AND logic`

---

### Step 8: Multi-Page Crawling
**Goal**: Crawl multiple pages from website

**TDD Approach:**
1. Write test: `test_crawler.py::test_crawl_multiple_pages()`
2. Add: URL queue, visited tracking, depth limit
3. Commit: `feat(crawler): implement multi-page crawling`

---

### Step 9: Better Error Handling
**Goal**: Handle network failures, malformed HTML

**TDD Approach:**
1. Write test: `test_crawler.py::test_handle_network_timeout()`
2. Add: Try-catch blocks, retry logic
3. Commit: `feat(crawler): add error handling for network failures`

---

### Step 10: Word Statistics in Index
**Goal**: Track frequency and position of words

**TDD Approach:**
1. Write test: `test_indexer.py::test_word_frequency_tracking()`
2. Modify index structure to store stats
3. Commit: `feat(indexer): track word frequency and position`

---

**After Phase 2 Git Log:**
```
commit a1b2c3d feat(indexer): track word frequency and position
commit d4e5f6g feat(crawler): add error handling for network failures
commit h7i8j9k feat(crawler): implement multi-page crawling
commit l0m1n2o feat(search): implement multi-word search with AND logic
commit p3q4r5s feat(indexer): implement index persistence
```

---

## Phase 3: Advanced Features (Days 6-7)

### Step 11: Case-Insensitive Search
**Goal**: Treat "Good", "good", "GOOD" as same word

**TDD Approach:**
1. Write test: `test_search.py::test_case_insensitive_search()`
2. Add: `.lower()` to word processing
3. Commit: `feat(search): implement case-insensitive keywords`

---

### Step 12: TF-IDF Ranking
**Goal**: Rank results by relevance using TF-IDF algorithm

**TDD Approach:**
1. Write test: `test_search.py::test_tfidf_ranking_order()`
2. Implement: TF-IDF scoring formula
3. Commit: `feat(search): add TF-IDF relevance ranking`

---

### Step 13: Query Suggestions
**Goal**: Suggest corrections for misspelled words

**TDD Approach:**
1. Write test: `test_search.py::test_query_suggestion()`
2. Implement: Edit distance (Levenshtein)
3. Commit: `feat(search): add query suggestions for typos`

---

### Step 14: Integration Tests
**Goal**: Test full workflow: crawl → index → search

**TDD Approach:**
1. Write test: `test_integration.py::test_full_workflow()`
2. Create full end-to-end flow
3. Commit: `test(integration): add full workflow integration test`

---

**After Phase 3 Git Log:**
```
commit t6u7v8w test(integration): add full workflow integration test
commit x9y0z1a feat(search): add query suggestions for typos
commit b2c3d4e feat(search): add TF-IDF relevance ranking
commit f5g6h7i feat(search): implement case-insensitive keywords
```

---

## Phase 4: Quality & Polish (Days 8-9)

### Step 15: Comprehensive Test Coverage
**Goal**: Reach 85%+ test coverage

**TDD Approach:**
1. Run: `pytest --cov=src`
2. Identify gaps
3. Add tests for edge cases
4. Commit: `test: increase coverage to 85%`

---

### Step 16: Type Hints & Docstrings
**Goal**: Add professional-grade documentation

**Commits Should Be:**
```
commit refactor(crawler): add type hints and docstrings
commit refactor(indexer): add type hints and docstrings
commit refactor(search): add type hints and docstrings
```

**Example Format:**
```python
def find_word(self, word: str) -> List[str]:
    """
    Find all pages containing a word.
    
    Time Complexity: O(1) lookup
    Space Complexity: O(k) where k = pages with word
    
    Args:
        word: The search term (lowercase)
    
    Returns:
        List of page URLs, empty if word not found
    """
```

---

### Step 17: Performance Optimization
**Goal**: Optimize indexing and search speed

**Commits:**
```
commit perf(indexer): use defaultdict for faster aggregation
commit perf(search): optimize set intersection for large queries
```

---

### Step 18: Complete README
**Goal**: Professional documentation

**Commit:**
```
commit docs: write comprehensive README with usage examples
```

---

### Step 19: Architecture Documentation
**Goal**: Design decisions and trade-offs

**Commit:**
```
commit docs: add ARCHITECTURE.md with design rationale
```

---

**After Phase 4:**
```
commit t1u2v3w docs: add ARCHITECTURE.md with design rationale
commit x4y5z6a docs: write comprehensive README with usage examples
commit b7c8d9e perf(search): optimize set intersection for large queries
commit f0g1h2i perf(indexer): use defaultdict for faster aggregation
commit j3k4l5m refactor(search): add type hints and docstrings
commit n6o7p8q refactor(indexer): add type hints and docstrings
commit r9s0t1u refactor(crawler): add type hints and docstrings
commit v2w3x4y test: increase coverage to 85%
```

---

## Phase 5: Final Video Prep (Day 10)

### Step 20: Create Video Demonstration
- Record live demo of all 4 commands
- Show code walkthrough
- Explain design decisions
- Demonstrate testing
- Evaluate GenAI usage
- Discuss research evidence

---

## Commit Naming Convention

```
feat:    New feature (feat(crawler): ...)
fix:     Bug fix (fix(indexer): ...)
test:    Test additions (test(search): ...)
refactor: Code restructuring (refactor(crawler): ...)
perf:    Performance improvement (perf(search): ...)
docs:    Documentation (docs: add README)
```

---

## Timeline

| Phase | Days | Key Features |
|-------|------|--------------|
| 1. Foundation | 1-2 | Crawler, Indexer, Search basics, CLI |
| 2. Core | 3-5 | Multi-page, Multi-word, Error handling |
| 3. Advanced | 6-7 | TF-IDF, Query suggestions, Integration |
| 4. Quality | 8-9 | Tests, Docs, Optimization |
| 5. Video | 10 | Record & submit |

---

## AI Usage Tracking

**Remember to log AI usage in:**
- `/notes/AI_USAGE_LOG.md`
- Track what each step used AI for
- Note what was fixed/modified
- Learning insights

---

## After Each Step

1. ✅ Write tests
2. ✅ Write minimal code to pass tests
3. ✅ Run tests (`pytest tests/`)
4. ✅ Update AI_USAGE_LOG if AI was involved
5. ✅ Commit with semantic message
6. ✅ Move to next step

---

## End Result

When complete, your git history will show:
- **20+ commits** showing incremental development
- **Each commit** is a working, tested feature
- **Professional progression** from basic to advanced
- **Clear evidence** of TDD and planning
- **Research implications** through RESEARCH.md

This demonstrates the **80-100 band criteria**:
✅ Professional Git workflow with semantic commits
✅ TDD approach with comprehensive tests
✅ Incremental development (not rushing)
✅ Evidence of research and planning
✅ Clean, documented code

