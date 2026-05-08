# AI Usage Log & Critical Evaluation

## Overview
This document tracks all AI tool usage throughout the development of the Search Engine Tool project. It serves as the foundation for the GenAI critical evaluation section of the video demonstration (15% of grade).

---

## AI Tools Declared
- **Tool Name**: GitHub Copilot (University of Leeds Secure Copilot Access)
- **Usage Scope**: Code generation, test suite design, error handling patterns, architecture decisions, debugging
- **Start Date**: 2026-04-01 (Project Start)
- **Status**: Active through Phase 2 Step 4 (8 April 2026)
- **Compliance Note**: Using only the University's secure Copilot access as per assignment brief requirements

---

## Usage Entries

### Entry Template
```
**Date**: [YYYY-MM-DD]
**Task**: [What component/task?]
**AI Tool**: [Which tool?]
**Purpose**: [Why did you use it?]
**What AI Generated/Suggested**: [Brief description of the output]
**Did It Help?**: [Yes/No/Partially]
**Details**:
  - What worked well:
  - What didn't work:
  - What you had to fix/modify:
  - Learning insights:
```

---

## Entry Log

### Entry 1: Phase 1, Step 1 - Basic Crawler Implementation

**Date**: 2026-04-08  
**Task**: Implement basic web crawler with fetch_page() and extract_text()  
**AI Tool**: GitHub Copilot (code structure suggestions)  
**Purpose**: Generate initial boilerplate for requests/BeautifulSoup integration  

**What AI Generated**: 
- Basic request.get() pattern with error handling
- BeautifulSoup parsing with get_text() method

**Did It Help?**: Yes  
**Details**:
- What worked well: Quick scaffolding of standard HTTP + HTML parsing patterns
- What didn't work: None - code was immediately functional
- What you had to fix: Only adjusted the test assertion (mock data mismatch)
- Learning insights: Requests library is straightforward; BeautifulSoup's get_text() handles tag removal cleanly

**Code Quality Assessment**: AI-generated code was production-ready with proper error handling (raise_for_status())

---

### Entry 2: Phase 1, Step 1 - Error Handling & Test Expansion

**Date**: 2026-04-09  
**Task**: Add comprehensive error handling with try/except blocks and expand test suite  
**AI Tool**: GitHub Copilot (test case generation and refactoring guidance)  
**Purpose**: Ensure production-grade error handling for network issues and write comprehensive test coverage

**What AI Generated**: 
- Expanded test suite with 9 error handling tests covering timeout, HTTP errors, connection errors
- Input validation tests for None, non-string, and empty string inputs
- Integration tests that connect to real website (quotes.toscrape.com)
- Comprehensive try/except structure with specific exception types

**Did It Help?**: Yes, but required debugging  
**Details**:
- What worked well: 
  - AI quickly generated all test scenarios (timeout, 404, 500, connection errors)
  - Test structure and assertions were correct and well-organized
  - Error handling code pattern was idiomatic Python
  - All 13 tests designed properly
  
- What didn't work: 
  - Initial HTTP error mocks failed because HTTPError objects lacked .response attribute
  - Mock HTTPError wasn't created with proper response object structure
  
- What you had to fix: 
  - Updated HTTPError mock tests to attach proper response object: `http_error.response = mock_response`
  - This taught me about how requests.exceptions work - they carry the response object
  - Had to understand mock.Mock() properties to create realistic error scenarios
  
- Learning insights: 
  - Real-world error handling requires understanding library specifics (requests.HTTPError structure)
  - Mocking is harder than implementing - you need exact knowledge of what the library does
  - Integration tests should skip gracefully if network unavailable
  - Defensive programming (validation in extract_text) catches bugs early

**Code Quality Assessment**: AI generated solid test patterns, but mistakes in mock objects revealed deeper API knowledge gaps that required manual fixing. This is valuable learning - AI can structure tests, but domain knowledge (how requests library works) is human responsibility.

---

### Entry 3: Phase 1, Step 2 - Politeness Window Implementation

**Date**: 2026-04-09  
**Task**: Add 6-second politeness delay between requests (ethical scraping)  
**AI Tool**: GitHub Copilot (feature design and test structure)  
**Purpose**: Implement politeness window to respect target website's server load

**What AI Generated**:
- Politeness window test suite (3 tests for default, custom, and disabled delays)
- Implementation pattern with time.sleep() before fetch
- Fixture design for mocking time.sleep to prevent test delays
- Documentation for respectful web scraping practice

**Did It Help?**: Yes, very effective  
**Details**:
- What worked well:
  - AI instantly understood the requirement and test pattern needed
  - Generated proper mock fixture structure (autouse=True)
  - Tests were well-organized and covered edge cases (delay=0 disabling)
  - Implementation was straightforward and idiomatic
  - All 3 politeness tests passed on first try
  
- What didn't work:
  - Initial test run was slow because time.sleep wasn't being mocked globally
  - Had to add autouse fixture to conftest.py to fix this
  
- What you had to fix:
  - Added autouse=True to mock_time_sleep fixture for auto-application
  - Removed flaky timing integration test (mock would interfere anyway)
  - Updated test documentation to reflect Step 2

- Learning insights:
  - Fixtures with autouse=True are powerful for cross-cutting concerns
  - Mocking library calls globally prevents performance penalties in tests
  - Politeness is a design decision, not just politeness - it prevents IP bans
  - Test infrastructure improvements (fixtures) deserve commits too

**Code Quality Assessment**: AI generated production-ready code on first try. The politeness implementation is simple but AI's fixture design was particularly good - it solved the test performance problem elegantly without me asking for it. This is an example of AI recognizing context (time.sleep calls → tests will be slow → need autouse fixture).

---

### Entry 4: Phase 1, Step 3 - Basic Indexer Setup

**Date**: 2026-04-09  
**Task**: Implement basic inverted index for single-word search  
**AI Tool**: GitHub Copilot (test design and implementation structure)  
**Purpose**: Build foundation for document search capability

**What AI Generated**:
- Comprehensive test suite (11 tests covering all indexer functionality)
- Inverted index data structure design (word -> document IDs mapping)
- Implementation of add_document, build_index, and search methods
- Proper handling of case-insensitivity, punctuation, deduplication

**Did It Help?**: Yes, very much  
**Details**:
- What worked well:
  - AI understood inverted index concept immediately
  - Generated well-organized test suite with multiple scenarios
  - Implementation was clean, efficient, and properly documented
  - Reused existing tokenize() utility correctly (DRY principle)
  - All 11 tests passed on first try with no fixes needed
  - Code structure matched production requirements perfectly
  
- What didn't work:
  - None - code was immediately functional and well-designed
  
- What you had to fix:
  - Nothing required - implementation was complete and correct
  
- Learning insights:
  - AI handles domain concepts well (inverted index is a known CS pattern)
  - Using sets internally then converting to lists is a good pattern
  - Separating add_document and build_index phases is more flexible
  - The tokenize utility reuse shows importance of factoring utilities
  - Index operations: add O(1), build O(n*m), search O(1)

**Code Quality Assessment**: Best result yet - AI generated comprehensive test suite and production-ready implementation with zero modifications needed. This demonstrates that for well-established CS patterns (like inverted indexes), AI can generate near-optimal code. The key difference from previous entries: this is a self-contained module with clear requirements, unlike integration challenges of previous steps.

---

### Entry 5: Git Workflow Refinement - Branch & Merge Strategy

**Date**: 2026-04-09  
**Task**: Establish proper git branching strategy for organized feature development  
**AI Tool**: Human decision with AI scaffolding support  
**Purpose**: Improve code organization, merge history clarity, and coursework documentation

**What We Discovered**:
- Initial approach mixed Steps 1-4 (Crawler + Indexer + Search) into single `feat/crawler-basic` branch
- This works functionally but produces unclear merge history
- Lesson: architectural features should align with branch boundaries

**What Was Implemented**:
```
Smart approach:
  Phase 1 (Steps 1-4) → Single consolidated feat/crawler-basic branch
    ✅ Merges to main after tests pass
  
  Phase 1.5 (Step 5: CLI) → New feat/cli-basic branch  
    → Will merge to main when complete
  
  Future phases:
    feat/persistence-advanced → Phase 2
    feat/multiword-search → Phase 2  
    feat/tfidf-ranking → Phase 3
    etc.
```

**Did It Help?**: Yes, process decision  
**Details**:
- What worked well:
  - Consolidating related steps (crawler/indexer/search) makes logical sense
  - They're all interdependent (each builds on previous)
  - Separating CLI as new branch keeps UI logic isolated
  - Clear branch naming enables self-documenting history
  - Makes coursework video explanation easier: "Feature X adds Y"
  
- What didn't work:
  - Didn't think about branch organization early enough
  - Started accumulating features without planning boundaries
  
- What you had to fix:
  - Manually merged feat/crawler-basic to main
  - Created fresh feat/cli-basic for next phase
  
- Learning insights:
  - Branch strategy should match architectural layers (transport, storage, search, ui)
  - One-feature-per-branch discipline prevents git history from becoming noise
  - "Logical feature" boundaries != line count - it's about dependencies
  - Proper organization helps reviewers understand progression

**Code Quality Assessment**: Process architecture, not code style. Good branching strategy is invisible when it works - making review/history clear. For coursework presentation, clear git history shows methodical progression through problem-solving phases.

**Strategy Going Forward (FOR REAL THIS TIME):**
1. Each major feature gets its own branch: `feat/[feature-name]`
2. Semantic commits WITHIN branch (test → implementation → verify)
3. When feature complete AND all tests pass: merge to main
4. Branch naming convention:
   - `feat/cli-basic` - Step 5
   - `feat/persistence-advanced` - Phase 2 feature
   - `feat/multiword-search` - Phase 2 feature
   - `feat/tfidf-ranking` - Phase 3 feature
5. Merge commits create logical story in history for presentation

---

### Entry 6: Phase 1, Step 5 - CLI Implementation & Error Handling

**Date**: 2026-04-09  
**Task**: Build interactive CLI (REPL) with comprehensive command orchestration and error handling  
**AI Tool**: GitHub Copilot (method scaffolding, error handling patterns, REPL design)  
**Purpose**: Create user-facing interface to orchestrate Crawler → Indexer → Search workflow

**What We Discovered**:
- Error handling in CLIs requires thought about multiple failure points
- Interactive REPL has different error model than unit tests
- User experience matters as much as correctness
- Each layer (URL input, indexing, searching) needs isolated error handling

**What Was Implemented**:

**CLI Class Methods (5 total):**
1. `__init__`: Validates crawler/indexer/search components + checks indexer is built
2. `build_index()`: Fetches website, builds index, returns doc count
3. `search_query()`: Executes search with query validation + result checking
4. `display_results()`: Formats results with doc_id + snippet + error recovery
5. `run()`: Interactive REPL loop with URL prompt → indexing → search loop

**Error Handling Strategy** (Makes this production-quality):
- **Input Validation**: Type checking, None checks, empty string checks at EVERY layer
- **Component Health**: Validates components have required methods/attributes
- **Data Integrity**: Checks fetched content not empty, index not empty, results properly formatted
- **Error Categories**: ValueError, RuntimeError, TypeError, generic Exception → clear categorization
- **Error Messages**: Specific messages showing what/where/why failed (not just "error!")
- **Graceful Degradation**: 
  - One bad query doesn't break REPL (continues loop)
  - Individual result format errors don't crash results display
  - Keyboard interrupt/EOF handled separately with friendly messages
- **User Feedback**: Visual indicators (✓ for success, ✗ for errors)

**Test Coverage** (29 tests, all passing):
- 6 init tests: component validation, built check
- 5 build_index tests: URL validation, crawler/indexer error handling
- 6 search_query tests: query validation, search execution, error propagation
- 5 display_results tests: result formatting, empty results, type validation
- 6 run tests: REPL flow, quit/EOF, error recovery, empty queries
- 1 integration test: full end-to-end workflow

**Code Quality Assessment**: High production value. Error handling went from basic to production-grade:
- **Before**: Basic happy-path implementation
- **After**: Defensive programming with error categories, user-friendly messages, recovering from partial failures

This teaches the grading rubric about error handling being a design discipline, not just catching exceptions.

**Lessons for Grader (Video talking points):**
- Error handling is ~40% of production code quality
- REPL requires different error model than function testing
- Type safety matters (checking isinstance, hasattr)
- User-facing systems need visual/textual feedback
- Component isolation (each error at right layer) prevents cascade failures

---

### Entry 7: Phase 2 Step 1 - Persistence (Save/Load Index & Documents)

**Date**: 2026-04-05  
**Task**: Implement JSON persistence for index and documents (save/load functionality)  
**AI Tool**: GitHub Copilot (JSON serialization, file I/O patterns)  
**Purpose**: Enable index saving to disk and reloading from saved state  

**What AI Generated**:
- JSON serialization/deserialization logic for inverted index
- Atomic file writing pattern (write to temp, then rename)
- Checkpoint system for recovery from interruptions
- Document storage with file paths and metadata

**Did It Help?**: Yes  
**Details**:
- What worked well:
  - AI understood atomic file operations importance
  - Generated proper try/finally for temp file cleanup
  - File I/O patterns were idiomatic and safe
  - All 26 tests passed on first implementation
  
- What didn't work:
  - None - implementation was solid
  
- What you had to fix:
  - Added checkpoint recovery logic (user insight)
  - Enhanced metadata tracking in documents
  
- Learning insights:
  - Atomic file operations prevent data corruption on crash
  - JSON is suitable for simple index structures
  - Metadata tracking (timestamps, checksums) aids debugging

**Test Coverage**: 26 tests (all passing)
- Save/load index
- Save/load documents
- Checkpoint creation and recovery
- Error handling for disk I/O

---

### Entry 8: Phase 2 Step 2 - Multi-Word Search (AND/OR Logic)

**Date**: 2026-04-05  
**Task**: Implement boolean query processing (AND/OR operators)  
**AI Tool**: GitHub Copilot (parsing algorithms, set operations)  
**Purpose**: Enable complex queries like "love AND beauty" or "dream OR hope"  

**What AI Generated**:
- Query parser with operator recognition
- Set operations for AND (intersection) and OR (union)
- Result ranking and deduplication
- Parentheses support for precedence

**Did It Help?**: Yes, very effective  
**Details**:
- What worked well:
  - AI understood boolean algebra immediately
  - Set intersection/union operations are elegant
  - Parser handled operator precedence correctly
  - All 33 tests passed on first try
  
- What didn't work:
  - None - algorithmic approach was optimal
  
- What you had to fix:
  - Added result ranking by frequency
  - Enhanced error messages for malformed queries
  
- Learning insights:
  - Set operations naturally map to boolean logic
  - Query parsing is solved problem (tokenize → parse → execute)
  - Ranking matters as much as correctness

**Test Coverage**: 33 tests (all passing)
- AND queries (intersection)
- OR queries (union)
- Mixed AND/OR precedence
- Error handling for invalid operators
- Empty result sets
- Result ranking

---

### Entry 9: Phase 2 Step 3 - Multi-Page Crawler (Pagination Support)

**Date**: 2026-04-06  
**Task**: Extend crawler to fetch multiple pages with automatic pagination detection  
**AI Tool**: GitHub Copilot (pagination patterns, URL manipulation)  
**Purpose**: Crawl entire website (up to N pages) instead of just first page  

**What AI Generated**:
- Next page URL detection ("Next" button parsing)
- Pagination loop with configurable limit
- Rate limiting integration with politeness window
- Progress tracking (pages fetched count)

**Did It Help?**: Yes  
**Details**:
- What worked well:
  - AI recognized common pagination patterns
  - URL construction logic was robust
  - Integration with existing politeness window was seamless
  - All 24 tests passed
  
- What didn't work:
  - None - pagination logic was correct
  
- What you had to fix:
  - Added configurable page limit parameter
  - Enhanced error recovery for broken pagination
  
- Learning insights:
  - Pagination detection is heuristic-based ("Next" button patterns vary)
  - Rate limiting becomes critical at scale
  - Progress tracking helps with long-running crawls

**Test Coverage**: 24 tests (all passing)
- Next page URL detection
- Multi-page fetching
- Pagination loop termination
- Rate limiting enforcement
- Progress tracking
- Edge cases (no next button, cycles)

---

### Entry 10: Phase 2 Step 4 - Word Frequency Analysis ⭐ JUST COMPLETED

**Date**: 2026-04-08  
**Task**: Implement word frequency tracking and document statistics  
**AI Tool**: GitHub Copilot (frequency algorithms, statistics)  
**Purpose**: Provide word frequency data for document analysis and future TF-IDF ranking  

**What AI Generated**:
- Frequency calculation algorithm (tokenize + count)
- Top-N words sorting
- Document length statistics
- Case-insensitive word matching

**Did It Help?**: Yes  
**Details**:
- What worked well:
  - AI understood frequency data structures immediately
  - Algorithm for top-N words was efficient (good sorting)
  - All 24 tests passed on first implementation
  - Code integrated seamlessly with existing indexer
  
- What didn't work:
  - None - implementation was correct
  
- What you had to fix:
  - None - code was production-ready
  
- Learning insights:
  - Frequency counting is O(n) per document
  - Using dict comprehension is more Pythonic than loops
  - Sorting by frequency is foundation for ranking algorithms

**Test Coverage**: 24 tests (all passing)
- Initialization with indexer validation (4 tests)
- Frequency calculation across documents (4 tests)
- Case-insensitive word lookup (6 tests)
- Top-N word retrieval with sorting (6 tests)
- Document length calculation (3 tests)
- Integration test (1 test)

**Implementation Details**:
- `__init__(indexer)`: Validates indexer, initializes frequency dict
- `calculate_frequencies()`: Dict[doc_id → Dict[word → count]]
- `get_word_frequency(word, doc_id)`: Case-insensitive lookup
- `get_top_words(doc_id, limit=10)`: Sorted list of top words
- `get_document_length(doc_id)`: Sum of word frequencies

**Commits Made**:
```
feat(word-frequency): implement __init__ - 4 tests pass
feat(word-frequency): implement calculate_frequencies - 4 tests pass
feat(word-frequency): implement get_word_frequency - 6 tests pass
feat(word-frequency): implement get_top_words - 6 tests pass
feat(word-frequency): implement get_document_length - 3 tests pass
feat(Phase 2 Step 4): implement word frequency analysis - 24 tests pass (merged to main)
```

---

### Entry 11: Integration Testing with Real Website

**Date**: 2026-04-08
**Task**: Write and run integration tests against live quotes.toscrape.com
**AI Tool**: GitHub Copilot (University of Leeds Secure Copilot Access)
**Purpose**: Verify all components work end-to-end with real HTTP requests

**What AI Generated**:
- 35 integration tests across 9 test classes covering the full pipeline
- Discovered critical bug: MultiwordSearch calling non-existent `search_query()` method
- Fixed bug: changed `self.search.search_query(word)` → `self.search.search(word)`
- Fixed 0-based doc_id references (indexer starts at 0, tests initially assumed 1)

**Did It Help?**: Yes
**Details**:
  - What worked well: AI generated comprehensive real-world test scenarios; caught a bug that unit tests missed because mocks hid the wrong method name
  - What didn't work: Initial doc_id assumptions were wrong (0-based vs 1-based)
  - What you had to fix/modify: Changed 6 test assertions from doc_id=1 to doc_id=0; fixed MultiwordSearch method call
  - Learning insights: Integration tests catch bugs that mocks hide; real HTTP tests require politeness delays (6s); 0-based vs 1-based indexing is a common source of bugs

**Test Coverage**: 35 tests (all passing, ~24s runtime with real HTTP)
- Real crawler fetch (6 tests)
- Real indexer (5 tests)
- Real search (4 tests)
- Real multi-page crawler (4 tests)
- Real multi-word search (4 tests)
- Real word frequency (4 tests)
- Real multi-page indexer (3 tests)
- Real persistence (3 tests)
- Real full pipeline (2 tests)

**Commits Made**:
```
fix(multiword-search): fix search_query -> search method call bug
feat(integration): add 35 real website integration tests (merged to main)
```

---

### Entry 12: CLI Rewrite to Match Assignment Brief

**Date**: 2026-04-08
**Task**: Rewrite CLI to implement the 4 commands required by COMP3011 coursework brief
**AI Tool**: GitHub Copilot (University of Leeds Secure Copilot Access)
**Purpose**: Make CLI actually work end-to-end with real website using required command structure

**What AI Generated**:
- Complete CLI rewrite with `build`, `load`, `print`, `find` commands
- New `src/main.py` entry point (`python -m src.main`)
- 26 new unit tests replacing 29 old tests that tested defunct API
- REPL with command parsing, help text, error handling

**Did It Help?**: Yes
**Details**:
  - What worked well: AI identified that old CLI was fundamentally broken (required pre-built components, no build/load/print/find commands, single-page only); generated complete working CLI matching brief
  - What didn't work: Old tests were entirely incompatible with new API - needed full rewrite, not incremental updates
  - What you had to fix/modify: Verified all 4 commands work with real website via piped input; confirmed load restores previously built index
  - Learning insights: CLI design should start from the user-facing requirements (the brief's 4 commands), not from internal component architecture; a no-arg constructor that bootstraps internally is cleaner than requiring pre-built dependencies

**Test Coverage**: 26 tests (all passing)
- CLI initialization (4 tests)
- Build command with mocked crawling (3 tests)
- Load command with file I/O (4 tests)
- Print command with index lookup (4 tests)
- Find command with single/multi-word search (5 tests)
- REPL loop (6 tests: quit, exit, help, unknown command, Ctrl+C, EOF)

**Implementation Details**:
- `CLI()`: No-arg constructor, creates Crawler internally
- `build(max_pages=10)`: MultiPageCrawler → Indexer → Persistence save
- `load()`: Restore index from data/index.json + data/documents.json
- `print_index(word)`: Case-insensitive inverted index lookup with frequency stats
- `find(query)`: Single or multi-word AND search with context snippets
- `run()`: Interactive REPL parsing all 4 commands + help/quit

**Commits Made**:
```
feat(cli): rewrite CLI to match coursework brief (build/load/print/find commands)
```

---

### Entry 13: Phase 3 - TF-IDF Ranking Implementation

**Date**: 2026-04-08  
**Task**: Implement TF-IDF (Term Frequency - Inverse Document Frequency) ranking module  
**AI Tool**: GitHub Copilot (TDD implementation, algorithm guidance)  
**Purpose**: Add relevance-based ranking to search results (required for 80+ grade)

**What AI Generated**:
- TfIdf class skeleton with 5 methods: `__init__`, `calculate_tf`, `calculate_idf`, `calculate_tfidf`, `rank_documents`, `search`
- 35 tests across 6 test classes covering all methods
- Full implementation following strict TDD: skeleton → tests → implement each method → commit

**Did It Help?**: Yes  
**Details**:
  - What worked well: AI correctly implemented the mathematical formulas — TF = word count / total words, IDF = log(N / df), TF-IDF = TF * IDF; ranking logic with multi-word score summation was clean
  - What didn't work: Initial `__init__` replacement accidentally ate the `calculate_tf` method definition due to a string replacement collision — had to manually fix the missing `def` line
  - What you had to fix/modify: Fixed the replacement collision; verified all 35 tests pass with exact mathematical assertions (pytest.approx)
  - Learning insights: TF-IDF is elegant — common words (IDF→0) get low scores naturally; rare document-specific words bubble up; the log function provides good discrimination between word frequencies

**Test Coverage**: 35 tests (all passing)
- TestTfIdfInit (4 tests): Validation of indexer dependency
- TestCalculateTf (6 tests): Term frequency per document, case-insensitive, edge cases
- TestCalculateIdf (6 tests): Inverse document frequency, rare vs common words
- TestCalculateTfIdf (6 tests): Combined score, zero cases, ranking property
- TestRankDocuments (7 tests): Multi-word queries, sorting, empty results, validation
- TestSearch (6 tests): Full search with snippets, limit, validation

**Commits Made** (TDD style):
```
feat(tfidf): add TfIdf class skeleton with 5 methods
test(tfidf): add 35 tests for TfIdf class (all failing against skeleton)
feat(tfidf): implement __init__ - 4 tests pass
feat(tfidf): implement calculate_tf - 6 tests pass
feat(tfidf): implement calculate_idf - 6 tests pass
feat(tfidf): implement calculate_tfidf - 6 tests pass
feat(tfidf): implement rank_documents - 7 tests pass
feat(tfidf): implement search - all 35 tests pass
```

---

### Entry 14: Phase 3 - TF-IDF CLI Integration

**Date**: 2026-04-08  
**Task**: Wire TF-IDF ranking into CLI find command  
**AI Tool**: GitHub Copilot (integration, test updates)  
**Purpose**: Replace unranked find results with TF-IDF ranked output showing relevance scores

**What AI Generated**:
- Updated CLI: import TfIdf, add `self.tfidf` to init and wiring, replace `find()` body with `self.tfidf.search(query)`
- Updated tests: added `score` field assertion, ranking order test, new `test_init_tfidf_is_none`
- Output format: numbered results with `[score: 0.1234]` prefix

**Did It Help?**: Yes, but required test fixture fixes  
**Details**:
  - What worked well: Integration was clean — TfIdf.search() already returns `{doc_id, score, snippet}` which is exactly what the CLI needs; removed the old manual search+multiword branching code
  - What didn't work: Test fixtures used "good" as search term, but "good" appeared in ALL test documents → IDF = log(2/2) = 0 → TF-IDF = 0 → no results. This is mathematically correct but broke the test assertion
  - What you had to fix/modify: Changed test search terms from "good" (ubiquitous) to "friends" (unique to one doc) so TF-IDF produces non-zero scores; this is actually a great insight into how TF-IDF works — common words are inherently down-weighted
  - Learning insights: TF-IDF's mathematical properties directly affect test design; you can't test relevance with words that appear everywhere because IDF correctly scores them as zero

**Test Coverage**: 28 tests (all passing, up from 26 — added `test_init_tfidf_is_none` and `test_find_results_ranked_by_score`)

**Commits Made**:
```
feat(cli): wire TF-IDF into find command for ranked search results - 28 tests pass
```


### Entry 15: Exact Phrase Search Using Positional Index

**Date**: 2026-05-07  
**Task**: Add exact phrase search for quoted queries such as `find "good friends"`  
**AI Tool**: GitHub Copilot (University of Leeds Secure Copilot Access)  
**Purpose**: Add an advanced search feature beyond the base brief and demonstrate why the inverted index stores word positions, not just frequencies

**What AI Generated/Suggested**:
- A `rank_phrase()` method in `src/search.py`
- Tests for adjacent word matching, wrong word order, repeated phrases, case-insensitive input, and punctuation handling
- CLI routing so quoted queries use phrase search while unquoted queries still use AND search
- Updated help text and phrase-specific result metadata

**Did It Help?**: Yes, with manual fixes  
**Details**:
  - What worked well: The existing positional index made phrase search a small, explainable extension. The tests clearly distinguished `find good friends` from `find "good friends"`.
  - What didn't work: The first CLI version generated snippets around the first query word rather than the actual phrase occurrence. A test indentation mistake also caused one collection error.
  - What you had to fix/modify: Added `_get_phrase_snippet()` so phrase results display the exact phrase in context, then reran the targeted, unit, and full test suites.
  - Learning insights: Position lists make phrase search possible without rescanning every document from scratch. This is a practical reason real search engines use positional indexes.

**Test Coverage**: 304 tests passing after the change
- 269 local tests
- 35 live integration tests
- Added phrase-search tests in `tests/test_tfidf.py` and `tests/test_cli.py`

**Commits Made**:
```
feat(search): add exact phrase search
```


## Key Points for Video Critical Evaluation

Use this section to prepare the 30-second GenAI reflection in the video:
- AI helped most with boilerplate, test generation, and established algorithms such as inverted indexing and TF-IDF.
- AI was less reliable around integration details: mock objects, method-name assumptions, doc_id indexing, and output formatting needed manual checking.
- Integration tests were important because they caught problems that unit tests with mocks could hide.
- The exact phrase feature showed that the positional index was not just extra data; it enabled a real search-engine behaviour.
- The main learning point was that AI sped up implementation, but understanding came from debugging, testing, and explaining the code.


## Summary Stats as of 7 May 2026

| Aspect | Details |
|--------|---------|
| AI Tool Used | GitHub Copilot (University of Leeds Secure Access) |
| Total AI Usage Entries | 15 entries across all phases |
| Most Helpful For | Test case generation, known CS patterns, error handling, boolean logic, TF-IDF, phrase-search scaffolding |
| Most Problematic For | Mock details, integration assumptions, doc_id indexing, TF-IDF test fixture design, CLI output details |
| Current Test Result | 304 passing tests |
| Local Tests | 269 passing tests |
| Live Integration Tests | 35 passing tests |
| Coverage | 90% line coverage on local tests |
| Advanced Features | TF-IDF ranking and exact phrase search |
| Current Goal | Final documentation polish, video recording, and submission |
| Deadline | 8 May 2026 |


## Achievement Breakdown by Phase

### Phase 1: Foundation
- Crawler: HTTP fetching + BeautifulSoup parsing + 6s politeness window
- Indexer: Inverted index data structure with efficient O(1) lookup
- Search: Single-word queries with context snippets
- CLI: Interactive REPL with commands (build, load, find, print)

### Phase 2: Core Features
- **Persistence:** JSON save/load + checkpoint recovery
- **Multi-word search:** AND/OR boolean queries
- **Multi-page crawler:** Pagination detection and last-page stopping
- **Word frequency:** Document statistics and top-N words

### Integration Testing
- Real HTTP requests against live quotes.toscrape.com
- Full pipeline verification: crawl → index → search → persist → reload
- Bug discovery: MultiwordSearch calling non-existent method (caught by integration tests, hidden by mocks)
- 0-based doc_id validation against real data

### CLI Rewrite
- All 4 brief-mandated commands: build, load, print, find
- Entry point: `python -m src.main`
- Verified end-to-end with real website

### Phase 3: Advanced Features
- **TF-IDF ranking:** Term frequency, inverse document frequency, combined scoring, ranked search
- **CLI integration:** find command returns TF-IDF ranked results with relevance scores
- **Exact phrase search:** Quoted queries use position lists to match adjacent words in order
- Video demonstration (pending)

---

## Key Learning Outcomes from AI Collaboration

**What AI Excels At:**
1. Generating comprehensive test suites (edge cases, error scenarios)
2. Implementing well-established CS patterns (inverted indexes, boolean logic)
3. Fixture design and testing infrastructure
4. Error handling patterns and defensive programming
5. Algorithm optimization (set operations, sorting)

**Where Manual Effort Was Needed:**
1. Understanding library-specific details (requests.HTTPError structure)
2. Integration between components
3. Recovery logic and edge case handling
4. Performance optimization decisions
5. API design choices


## Final Reflection for Video

Overall, AI made the project faster to build but did not remove the need to understand the implementation. It was strongest when the task matched common programming patterns, such as writing tests, using Requests and BeautifulSoup, building an inverted index, and implementing TF-IDF scoring.

The main weaknesses appeared at integration boundaries. Some generated tests made wrong assumptions about mock objects or document IDs, and one integration bug was only found when the real pipeline was tested. This showed that generated code still needs manual verification.

The most useful learning came from debugging and improving AI suggestions. For example, the phrase-search feature made me understand why storing word positions matters: without positions, the tool can only check whether words appear somewhere in the same page; with positions, it can check whether the words appear next to each other in order.

For academic integrity, all AI use has been declared in this log. The code was tested, reviewed, and adapted rather than accepted blindly.