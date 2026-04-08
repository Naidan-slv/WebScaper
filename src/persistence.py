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
        try:
            if filepath is None:
                raise ValueError("Filepath cannot be None")
            if not isinstance(filepath, str):
                raise ValueError(f"Filepath must be string, got {type(filepath).__name__}")
            if not filepath.strip():
                raise ValueError("Filepath cannot be empty string")
            
            if not self.indexer.documents:
                raise ValueError("Documents are empty, nothing to save")
            
            # Convert documents to JSON-serializable format
            # Convert int keys to strings for JSON compatibility
            data = {str(k): v for k, v in self.indexer.documents.items()}
            
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
            raise OSError(f"Failed to write documents to {filepath}: {e}")
        except Exception as e:
            raise OSError(f"Unexpected error saving documents: {type(e).__name__}: {e}")

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
        try:
            if filepath is None:
                raise ValueError("Filepath cannot be None")
            if not isinstance(filepath, str):
                raise ValueError(f"Filepath must be string, got {type(filepath).__name__}")
            if not filepath.strip():
                raise ValueError("Filepath cannot be empty string")
            
            # Check if file exists
            if not Path(filepath).exists():
                raise FileNotFoundError(f"Documents file not found: {filepath}")
            
            # Load JSON file
            with open(filepath, "r") as f:
                data = json.load(f)
            
            if not isinstance(data, dict):
                raise ValueError(f"Documents must be dict, got {type(data).__name__}")
            
            return data
            
        except (ValueError, FileNotFoundError, json.JSONDecodeError) as e:
            raise e
        except (OSError, IOError) as e:
            raise FileNotFoundError(f"Failed to read documents from {filepath}: {e}")
        except Exception as e:
            raise Exception(f"Error loading documents: {type(e).__name__}: {e}")

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
        try:
            if dirpath is None:
                raise ValueError("Directory path cannot be None")
            if not isinstance(dirpath, str):
                raise ValueError(f"Directory path must be string, got {type(dirpath).__name__}")
            if not dirpath.strip():
                raise ValueError("Directory path cannot be empty string")
            
            # Create directory if it doesn't exist
            checkpoint_dir = Path(dirpath)
            checkpoint_dir.mkdir(parents=True, exist_ok=True)
            
            # Save index
            index_file = checkpoint_dir / "index.json"
            index_bytes = self.save_index(str(index_file))
            
            # Save documents
            docs_file = checkpoint_dir / "documents.json"
            docs_bytes = self.save_documents(str(docs_file))
            
            return {
                "index_file": index_bytes,
                "docs_file": docs_bytes
            }
            
        except ValueError as e:
            raise e
        except (OSError, IOError) as e:
            raise OSError(f"Failed to create checkpoint at {dirpath}: {e}")
        except Exception as e:
            raise OSError(f"Error saving checkpoint: {type(e).__name__}: {e}")

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
        try:
            if dirpath is None:
                raise ValueError("Directory path cannot be None")
            if not isinstance(dirpath, str):
                raise ValueError(f"Directory path must be string, got {type(dirpath).__name__}")
            if not dirpath.strip():
                raise ValueError("Directory path cannot be empty string")
            
            checkpoint_dir = Path(dirpath)
            
            # Check if directory exists
            if not checkpoint_dir.exists():
                raise FileNotFoundError(f"Checkpoint directory not found: {dirpath}")
            
            index_file = checkpoint_dir / "index.json"
            docs_file = checkpoint_dir / "documents.json"
            
            # Check if required files exist
            if not index_file.exists():
                raise FileNotFoundError(f"Index file not found in checkpoint: {index_file}")
            if not docs_file.exists():
                raise FileNotFoundError(f"Documents file not found in checkpoint: {docs_file}")
            
            # Load index
            index_data = self.load_index(str(index_file))
            
            # Load documents
            docs_data = self.load_documents(str(docs_file))
            
            return {
                "index": index_data,
                "documents": docs_data
            }
            
        except (ValueError, FileNotFoundError, json.JSONDecodeError) as e:
            raise e
        except Exception as e:
            raise Exception(f"Error loading checkpoint: {type(e).__name__}: {e}")
