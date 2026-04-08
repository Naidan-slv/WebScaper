"""
Search Engine Tool - Entry Point

COMP3011 Coursework 2: Search Engine Tool
Target Website: https://quotes.toscrape.com/

Usage:
    python -m src.main

Commands:
    build       - Crawl website, build index, save to file
    load        - Load saved index from file
    print <w>   - Print inverted index for a word
    find <q>    - Find pages containing search terms
    help        - Show available commands
    quit        - Exit the program
"""

from src.cli import CLI


def main():
    """Launch the search engine CLI."""
    cli = CLI()
    cli.run()


if __name__ == "__main__":
    main()
