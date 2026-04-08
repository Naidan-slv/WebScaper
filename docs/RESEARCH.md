# Search Engine Algorithm Research & Implementation

## Overview

This document outlines the algorithms, data structures, and modern search engine techniques used in the WebScaper project. It demonstrates research into professional search engine implementations and includes complexity analysis.

---

## Implemented Techniques

### 1. Inverted Index (Core Data Structure)

**What It Is:**
An inverted index maps words to the pages where they appear, along with metadata like frequency and position.

```
Word → {Page_A: [freq: 3, positions: [0, 15, 42]], Page_B: [freq: 1, positions: [7]]}
```

**Why This Approach:**
- **Time Complexity**: O(1) average lookup for a single word
- **Space Complexity**: O(W × D) where W = unique words, D = average document frequency
- **Research Background**: Standard technique used by Apache Lucene, Elasticsearch, and Google
- **Trade-off**: Higher memory usage during indexing, but O(1) query performance

**Historical Context:**
- First introduced in the 1960s for information retrieval systems
- Refined by Van Rijsbergen (1979) in "Information Retrieval"
- Remains the industry standard for modern search engines

---

### 2. Case-Insensitive Tokenization

**Implementation:**
All words converted to lowercase before indexing.

**Why It Matters:**
- **Recall Improvement**: Prevents missing relevant documents due to capitalization
- **User Experience**: Users don't need to match case exactly in queries
- **Industry Standard**: Google, Bing, and modern search engines normalize case

**Example:**
```
"Good" + "good" + "GOOD" → normalized to "good" → single index entry
```

---

### 3. Politeness Window & Respectful Crawling

**Requirement:** Minimum 6-second delay between requests

**Why It's Important:**
- **Ethical Crawling**: Prevents server overload
- **Legal Compliance**: Respects robots.txt and crawling regulations
- **Research Reference**: Best practices from SEO and web crawling literature

**Implementation:**
```python
time.sleep(6)  # Between successive requests
```

**Complexity Impact:**
- Crawling Time: O(n × 6) where n = number of pages
- This is acceptable for the demonstration scope

---

## Advanced Features (Beyond Requirements)

### 4. TF-IDF Ranking (Term Frequency - Inverse Document Frequency)

**Formula:**
```
TF-IDF(term, doc) = TF(term, doc) × IDF(term)

Where:
  TF(term, doc) = (frequency of term in doc) / (total terms in doc)
  IDF(term) = log(total documents / documents containing term)
```

**Why This Approach:**
- Ranks results by relevance, not just exact match
- Prevents common words (the, a, is) from dominating results
- Professional search engines use variations of TF-IDF as baseline

**Research Background:**
- Invented by Karen Sparck Jones (1972), foundational paper: "A Statistical Interpretation of Term Specificity"
- Modern variations: BM25, TF-IDF with cosine similarity

**Time Complexity:** O(k × log(n)) where k = result count, n = total documents
**Space Complexity:** O(k) for storing scores

---

### 5. Multi-Word Query Optimization

**Algorithm: Set Intersection with Early Termination**

```
Query: "good friends"
1. Find pages with "good": Set_A = {page_1, page_3, page_5, page_7, ...}
2. Find pages with "friends": Set_B = {page_2, page_3, page_8}
3. Intersection: Set_A ∩ Set_B = {page_3}
```

**Optimization: Process Rarest Word First**
```
If "good" appears in 100 pages and "friends" in 5 pages:
Start with intersection of 5 pages (smaller set) for efficiency
```

**Time Complexity:** O(m × min(n1, n2)) where m = query words, n1/n2 = posting list sizes
**Space Complexity:** O(min(n1, n2)) for temporary sets

---

### 6. Query Suggestions (Bonus Feature)

**Algorithm: Edit Distance (Levenshtein Distance)**

Detects typos and suggests corrections:
```
User types: "goo"
Suggestion: "good" (edit distance = 1)
```

**Time Complexity:** O(n × m) dynamic programming where n, m = word lengths
**Space Complexity:** O(n × m)

**Research:** Classic algorithm in computational linguistics, used by spell checkers

---

## Complexity Analysis Summary

| Operation | Time Complexity | Space Complexity | Notes |
|-----------|-----------------|------------------|-------|
| Crawl n pages | O(n × 6s) | O(p) | Respects politeness window; p = total pages |
| Build index (w words) | O(w × d) | O(w × d) | d = avg words per page |
| Single-word search | O(1) | O(1) | Direct inverted index lookup |
| Multi-word search (m words) | O(m × log(k)) | O(k) | k = results; set intersection |
| TF-IDF ranking | O(k × log(n)) | O(k) | n = total docs; sorts results |
| Query suggestion | O(n × m) | O(n × m) | Levenshtein distance calculation |

---

## Data Structures Used

### 1. Inverted Index: `Dict[str, Dict[str, dict]]`
```python
{
    "good": {
        "page_1": {"freq": 3, "positions": [0, 15, 42]},
        "page_3": {"freq": 1, "positions": [7]}
    }
}
```

### 2. Document Store: `Dict[str, str]`
Maps URLs to page content for re-ranking and context.

### 3. Cache: `Set[str]`
Tracks already-crawled URLs to prevent duplicates.

---

## Modern Search Engine Techniques Incorporated

1. **Error Resilience**: Handles network timeouts, malformed HTML, missing content
2. **Politeness & Ethics**: Respects server load and crawling best practices
3. **Normalization**: Case-insensitive search for better UX
4. **Ranking**: TF-IDF for relevance instead of simple matching
5. **Deduplication**: Prevents indexing duplicate content
6. **Caching**: Avoids re-crawling known URLs

---

## References & Further Reading

### Foundational Papers
- **Van Rijsbergen, C.J.** (1979). "Information Retrieval" - Classic IR textbook
- **Sparck Jones, K.** (1972). "A Statistical Interpretation of Term Specificity and its Application in Retrieval"
- **Brin, S. & Page, L.** (1998). "The Anatomy of a Large-Scale Hypertextual Web Search Engine" (Google's original paper)

### Modern Resources
- Apache Lucene: https://lucene.apache.org/ (Open-source search engine library)
- Elasticsearch Documentation: https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html
- Python NLTK: Natural Language Toolkit for tokenization and stemming

---

## Trade-offs & Design Decisions

### Why Inverted Index vs. Full-Text Scan?
- **Inverted Index**: O(1) lookup, higher memory
- **Full-Text Scan**: O(n) every query, lower memory

**Decision**: Inverted Index for better query performance (matches professional search engines)

### Why TF-IDF vs. Simple Frequency?
- **Simple Frequency**: Biased toward common words
- **TF-IDF**: Balances frequency and word uniqueness

**Decision**: TF-IDF for relevance (more useful results)

### Why Set Intersection for Multi-Word Queries?
- Efficient and mathematically correct for AND queries
- Easy to extend to OR/NOT queries if needed

---

## Future Enhancements

For production-grade implementation:
1. **Boolean Retrieval**: Support AND, OR, NOT operators
2. **Phrase Queries**: Exact phrase matching with position tracking
3. **Stemming/Lemmatization**: Normalize word forms (running → run)
4. **Caching**: Redis or in-memory cache for frequently queried words
5. **Distributed Indexing**: Sharding for large-scale crawls
6. **Query Expansion**: Synonyms for better recall
7. **Machine Learning**: Learning-to-rank models for personalized relevance

