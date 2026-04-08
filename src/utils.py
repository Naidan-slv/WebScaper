"""
Shared utilities for tokenization and common operations.

This module contains functions used across Crawler, Indexer, and Search classes
to maintain DRY principle and consistency.
"""

from typing import List
import re


def tokenize(text: str) -> List[str]:
    """
    Tokenize text into words and handle basic normalization.
    
    Converts to lowercase and splits on whitespace. Removes punctuation.
    
    Time Complexity: O(n) where n = length of text
    Space Complexity: O(n) for output list
    
    Args:
        text: Raw text to tokenize
    
    Returns:
        List of lowercase words without punctuation
    
    Example:
        >>> tokenize("Hello, World!")
        ['hello', 'world']
    """
    # Convert to lowercase
    text = text.lower()
    
    # Remove punctuation but keep apostrophes within words (don't -> dont)
    text = re.sub(r"[^\w\s]", "", text)
    
    # Split on whitespace
    words = text.split()
    
    # Remove empty strings
    words = [w for w in words if w]
    
    return words


def is_valid_url(url: str) -> bool:
    """
    Check if a string is a valid URL.
    
    Time Complexity: O(n) where n = length of URL
    Space Complexity: O(1)
    
    Args:
        url: String to validate
    
    Returns:
        True if valid URL format, False otherwise
    """
    # Basic URL validation
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP
        r'(?::\d+)?',  # optional port
        re.IGNORECASE
    )
    return bool(url_pattern.match(url))


def normalize_url(url: str) -> str:
    """
    Normalize a URL for comparison and storage.
    
    Removes trailing slashes and fragments.
    
    Time Complexity: O(n)
    Space Complexity: O(n)
    
    Args:
        url: URL to normalize
    
    Returns:
        Normalized URL
    """
    # Remove fragment (everything after #)
    url = url.split('#')[0]
    
    # Remove trailing slash (except for root)
    if url.endswith('/') and url.count('/') > 3:  # More than just http:// or https://
        url = url[:-1]
    
    return url
