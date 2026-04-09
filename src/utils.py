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
