# Architecture & Design

## Step 1: Crawler Wireframe

**What we're building:**
A Crawler class that can fetch a single web page and extract text.

**Two methods:**

1. `fetch_page(url)` → returns HTML string
   - Takes a URL like "https://quotes.toscrape.com/"
   - Makes HTTP GET request
   - Returns raw HTML
   - Handles errors (network failure, 404, etc.)

2. `extract_text(html)` → returns plain text string
   - Takes HTML string
   - Parses with BeautifulSoup
   - Extracts visible text like we'd see in browser
   - Cleans up whitespace

**Input/Output Example:**

```
fetch_page("https://quotes.toscrape.com/page/1/")
    ↓ (network request)
    ↓
    Returns: "<html><head>...</head><body><p>Quote text here...</p></body></html>"

extract_text(html_string)
    ↓ (BeautifulSoup parsing)
    ↓
    Returns: "Quote text here..."
```

**Why this first?**
- Simplest unit
- No dependencies on other classes yet
- Foundation for everything else
- Easy to test with mocked HTTP responses


