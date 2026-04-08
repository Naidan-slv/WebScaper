"""
Index persistence for the web scraper search engine.

Provides save/load functionality to persist index to disk.
- Saves inverted index in JSON format
- Saves documents in JSON format  
- Loads previously saved indexes
- Validates saved data integrity
"""

import json
from pathlib import Path


class Persistence:
    """Handle saving and loading inverted index to/from disk."""

    def __init__(self, indexer):
        """
        Initialize persistence handler with indexer.
        
        Args:
            indexer: Indexer instance to save/load to
            
        Raises:
            ValueError: If indexer is None
        """
        if indexer is None:
            raise ValueError("Indexer cannot be None")
        
        self.indexer = indexer

    def save_index(self, filepath):
        """
        Save inverted index to JSON file.
        
        Args:
            filepath (str): Path to save index file to
            
        Returns:
            int: Number of bytes written
            
        Raises:
            ValueError: If filepath invalid or index empty
            OSError: If file write fails
        """
        try:
            if filepath is None:
                raise ValueError("Filepath cannot be None")
            if not isinstance(filepath, str):
                raise ValueError(f"Filepath must be string, got {type(filepath).__name__}")
            if not filepath.strip():
                raise ValueError("Filepath cannot be empty string")
            
            if not self.indexer.index:
                raise ValueError("Index is empty, nothing to save")
            
            # Convert index to JSON-serializable format
            data = dict(self.indexer.index)
            
            # Write to file
            with open(filepath, "w") as f:
                json.dump(data, f, indent=2)
            
            # Return bytes written
            with open(filepath, "rb") as f:
                byte_count = len(f.read())
            
            return byte_count
            
        except ValueError as e:
            raise e
        except (OSError, IOError) as e:
            raise OSError(f"Failed to write index to {filepath}: {e}")
        except Exception as e:
            raise OSError(f"Unexpected error saving index: {type(e).__name__}: {e}")

    def load_index(self, filepath):
        """
        Load inverted index from JSON file.
        
        Args:
            filepath (str): Path to load index from
            
        Returns:
            dict: Loaded index data
            
        Raises:
            ValueError: If filepath invalid or file format invalid
            FileNotFoundError: If file doesn't exist
            json.JSONDecodeError: If JSON malformed
        """
        try:
            if filepath is None:
                raise ValueError("Filepath cannot be None")
            if not isinstance(filepath, str):
                raise ValueError(f"Filepath must be string, got {type(filepath).__name__}")
            if not filepath.strip():
                raise ValueError("Filepath cannot be empty string")
            
            # Check if file exists
            if not Path(filepath).exists():
                raise FileNotFoundError(f"Index file not found: {filepath}")
            
            # Load JSON file
            with open(filepath, "r") as f:
                data = json.load(f)
            
            if not isinstance(data, dict):
                raise ValueError(f"Index must be dict, got {type(data).__name__}")
            
            return data
            
        except (ValueError, FileNotFoundError, json.JSONDecodeError) as e:
            raise e
        except (OSError, IOError) as e:
            raise FileNotFoundError(f"Failed to read index from {filepath}: {e}")
        except Exception as e:
            raise Exception(f"Error loading index: {type(e).__name__}: {e}")

    def save_documents(self, filepath):
        """
        Save documents to JSON file.
        
        Args:
            filepath (str): Path to save documents to
            
        Returns:
            int: Number of bytes written
            
        Raises:
            ValueError: If filepath invalid or documents empty
            OSError: If file write fails
        """
        raise NotImplementedError

    def load_documents(self, filepath):
        """
        Load documents from JSON file.
        
        Args:
            filepath (str): Path to load documents from
            
        Returns:
            dict: Loaded documents (doc_id -> text)
            
        Raises:
            ValueError: If filepath invalid or file format invalid
            FileNotFoundError: If file doesn't exist
            json.JSONDecodeError: If JSON malformed
        """
        raise NotImplementedError

    def save_checkpoint(self, dirpath):
        """
        Save index and documents to directory (checkpoint).
        
        Args:
            dirpath (str): Directory to save checkpoint to
            
        Returns:
            dict: Summary of saved files {'index_file': bytes, 'docs_file': bytes}
            
        Raises:
            ValueError: If dirpath invalid
            OSError: If file write fails
        """
        raise NotImplementedError

    def load_checkpoint(self, dirpath):
        """
        Load index and documents from checkpoint directory.
        
        Args:
            dirpath (str): Directory to load checkpoint from
            
        Returns:
            dict: Summary of loaded files {'index': dict, 'documents': dict}
            
        Raises:
            ValueError: If dirpath invalid
            FileNotFoundError: If checkpoint files missing
            json.JSONDecodeError: If JSON malformed
        """
        raise NotImplementedError
