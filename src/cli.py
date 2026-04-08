"""
Basic CLI for the web scraper search engine.

Provides a command-line interface to:
- Build an inverted index from a website
- Search the index with queries
- Display results with context snippets
"""


class CLI:
    """Command-line interface for web scraper search engine."""

    def __init__(self, crawler, indexer, search):
        """
        Initialize CLI with crawler, indexer, and search components.
        
        Args:
            crawler: Crawler instance for fetching pages
            indexer: Indexer instance for building search index
            search: Search instance for executing queries
            
        Raises:
            ValueError: If any component is None
            RuntimeError: If indexer is not built
        """
        if crawler is None:
            raise ValueError("Crawler cannot be None")
        if indexer is None:
            raise ValueError("Indexer cannot be None")
        if search is None:
            raise ValueError("Search cannot be None")
        
        # Check if indexer has been built
        if not hasattr(indexer, "index"):
            raise RuntimeError("Indexer must have index attribute")
        if not indexer.index:
            raise RuntimeError("Indexer must be built before initializing CLI")
        
        self.crawler = crawler
        self.indexer = indexer
        self.search = search

    def build_index(self, url):
        """
        Fetch pages from URL and build search index.
        
        Args:
            url (str): Website URL to scrape and index
            
        Returns:
            int: Number of documents indexed
            
        Raises:
            ValueError: If URL is invalid or indexer fails to build
            Exception: If crawler fails to fetch pages
        """
        if url is None:
            raise ValueError("URL cannot be None")
        if not isinstance(url, str) or not url.strip():
            raise ValueError("URL must be a non-empty string")
        
        try:
            # Fetch page using crawler
            html = self.crawler.fetch_page(url)
            
            if not html:
                raise ValueError(f"Fetched content is empty from {url}")
            
            # Add document to indexer
            self.indexer.add_document(html)
            
            # Build the index
            self.indexer.build_index()
            
            # Return number of documents indexed
            doc_count = len(self.indexer.documents)
            if doc_count == 0:
                raise ValueError("Index was built but contains no documents")
            
            return doc_count
            
        except ValueError as e:
            # Re-raise validation errors
            raise e
        except AttributeError as e:
            raise RuntimeError(f"Indexer component missing required method: {e}")
        except Exception as e:
            raise Exception(f"Failed to build index from {url}: {type(e).__name__}: {e}")

    def search_query(self, query):
        """
        Execute search query and return results with snippets.
        
        Args:
            query (str): Search query (single or multiple words)
            
        Returns:
            list: Results with format [{'doc_id': int, 'snippet': str, 'text': str}, ...]
            
        Raises:
            ValueError: If query is invalid
        """
        try:
            if query is None:
                raise ValueError("Query cannot be None")
            if not isinstance(query, str):
                raise ValueError(f"Query must be a string, got {type(query).__name__}")
            if not query.strip():
                raise ValueError("Query cannot be empty or whitespace only")
            
            # Execute search through search component
            try:
                results = self.search.search_with_snippets(query.lower())
            except AttributeError as e:
                raise RuntimeError(f"Search component missing method: {e}")
            
            if not isinstance(results, list):
                raise TypeError(f"Search returned {type(results).__name__}, expected list")
            
            return results
            
        except (ValueError, RuntimeError, TypeError) as e:
            raise e
        except Exception as e:
            raise Exception(f"Search operation failed: {type(e).__name__}: {e}")

    def display_results(self, query, results):
        """
        Format and display search results to console.
        
        Args:
            query (str): Original search query
            results (list): Results from search_query()
            
        Returns:
            str: Formatted output string
        """
        try:
            if query is None:
                raise ValueError("Query cannot be None")
            if not isinstance(query, str):
                raise ValueError(f"Query must be string, got {type(query).__name__}")
            
            if results is None:
                results = []
            elif not isinstance(results, list):
                raise TypeError(f"Results must be list, got {type(results).__name__}")
            
            if not results:
                return f"No results found for '{query}'"
            
            output_lines = [f"Found {len(results)} result(s) for '{query}':", ""]
            
            for i, result in enumerate(results, 1):
                try:
                    if not isinstance(result, dict):
                        raise TypeError(f"Result {i} must be dict, got {type(result).__name__}")
                    
                    doc_id = result.get("doc_id", "?")
                    snippet = result.get("snippet", "")
                    
                    if not isinstance(snippet, str):
                        snippet = str(snippet)
                    
                    output_lines.append(f"{i}. Document ID: {doc_id}")
                    output_lines.append(f"   Snippet: {snippet}")
                    output_lines.append("")
                    
                except (TypeError, AttributeError) as e:
                    output_lines.append(f"{i}. [Error formatting result: {e}]")
                    output_lines.append("")
            
            return "\n".join(output_lines)
            
        except (ValueError, TypeError) as e:
            raise e
        except Exception as e:
            raise Exception(f"Error displaying results: {type(e).__name__}: {e}")

    def run(self):
        """
        Run interactive REPL for user queries.
        
        Workflow:
        1. Prompt user for website URL
        2. Build index
        3. Loop: Accept queries, display results
        4. Exit on "quit" or EOF
        """
        try:
            # Step 1: Get URL from user
            try:
                url = input("Enter website URL to index: ").strip()
            except (KeyboardInterrupt, EOFError):
                print("\nInterrupted. Exiting.")
                return
            except Exception as e:
                print(f"Error reading input: {e}")
                return
            
            if not url:
                print("Error: No URL provided. Exiting.")
                return
            
            # Step 2: Build index
            print(f"\nBuilding index from {url}...")
            try:
                doc_count = self.build_index(url)
                print(f"✓ Successfully indexed {doc_count} document(s)\n")
            except ValueError as e:
                print(f"✗ Validation error: {e}")
                return
            except RuntimeError as e:
                print(f"✗ Component error: {e}")
                return
            except Exception as e:
                print(f"✗ Failed to build index: {type(e).__name__}: {e}")
                return
            
            # Step 3: Accept queries
            print("Enter search queries (type 'quit' to exit):")
            while True:
                try:
                    query = input("\nQuery: ").strip()
                except (KeyboardInterrupt, EOFError):
                    print("\n\nInterrupted. Goodbye!")
                    return
                except Exception as e:
                    print(f"Error reading query: {e}")
                    continue
                
                # Check for quit command
                if query.lower() == "quit":
                    print("Goodbye!")
                    return
                
                # Skip empty queries
                if not query:
                    print("Please enter a search query.")
                    continue
                
                # Execute search
                try:
                    results = self.search_query(query)
                    output = self.display_results(query, results)
                    print(output)
                    
                except ValueError as e:
                    print(f"✗ Invalid query: {e}")
                except RuntimeError as e:
                    print(f"✗ Search component error: {e}")
                except TypeError as e:
                    print(f"✗ Type error in search: {e}")
                except Exception as e:
                    print(f"✗ Search failed: {type(e).__name__}: {e}")
                    
        except KeyboardInterrupt:
            print("\n\nInterrupted. Goodbye!")
        except EOFError:
            print("\n\nEnd of input. Goodbye!")
        except Exception as e:
            print(f"✗ Unexpected error in CLI: {type(e).__name__}: {e}")
