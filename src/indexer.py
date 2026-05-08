"""Indexing, tokenization, word-frequency, and persistence code."""

import json
import re
from pathlib import Path
from typing import List


def tokenize(text: str) -> List[str]:
    """Lowercase text, remove punctuation, and split into words."""
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    return [w for w in text.split() if w]


class Indexer:
    """Build and manage a positional inverted index."""

    def __init__(self):
        self.index = {}
        self.documents = {}
        self.urls = {}
        self.document_count = 0

    def add_document(self, text: str, url: str = None) -> int:
        doc_id = self.document_count
        self.documents[doc_id] = text
        if url is not None:
            self.urls[doc_id] = url
        self.document_count += 1
        return doc_id

    def build_index(self) -> None:
        """Build word -> doc_id -> frequency/positions."""
        self.index = {}

        for doc_id, text in self.documents.items():
            for position, token in enumerate(tokenize(text)):
                if token not in self.index:
                    self.index[token] = {}
                if doc_id not in self.index[token]:
                    self.index[token][doc_id] = {"frequency": 0, "positions": []}

                self.index[token][doc_id]["frequency"] += 1
                self.index[token][doc_id]["positions"].append(position)

    def search(self, query: str) -> list:
        query_normalized = query.lower().strip()
        if query_normalized in self.index:
            return sorted(self.index[query_normalized].keys())
        return []

    def get_index_entry(self, word: str) -> dict:
        word_normalized = word.lower().strip()
        if word_normalized in self.index:
            return self.index[word_normalized]
        return None

    def get_document(self, doc_id: int) -> str:
        return self.documents[doc_id]

    def get_document_url(self, doc_id: int) -> str:
        return self.urls.get(doc_id)


class WordFrequency:
    """Calculate word frequencies from a built indexer."""

    def __init__(self, indexer):
        if indexer is None:
            raise ValueError("Indexer cannot be None")
        if not indexer.documents or not indexer.index:
            raise ValueError("Indexer must be built with documents and index")

        self.indexer = indexer
        self.frequencies = {}

    def calculate_frequencies(self):
        self.frequencies = {}

        for doc_id, text in self.indexer.documents.items():
            word_freq = {}
            for word in tokenize(text):
                word_freq[word] = word_freq.get(word, 0) + 1
            self.frequencies[doc_id] = word_freq

        return self.frequencies

    def get_word_frequency(self, word, doc_id):
        if word is None:
            raise ValueError("Word cannot be None")
        if doc_id not in self.frequencies:
            raise KeyError(f"Document {doc_id} not found")

        word_lower = word.lower().strip()
        return self.frequencies[doc_id].get(word_lower, 0)

    def get_top_words(self, doc_id, limit=10):
        if doc_id not in self.frequencies:
            raise KeyError(f"Document {doc_id} not found")

        sorted_words = sorted(
            self.frequencies[doc_id].items(),
            key=lambda x: (-x[1], x[0]),
        )
        return [
            {"word": word, "frequency": freq}
            for word, freq in sorted_words[:limit]
        ]

    def get_document_length(self, doc_id):
        if doc_id not in self.frequencies:
            raise KeyError(f"Document {doc_id} not found")

        return sum(self.frequencies[doc_id].values())


class Persistence:
    """Save and load generated index/document JSON files."""

    def __init__(self, indexer):
        if indexer is None:
            raise ValueError("Indexer cannot be None")
        self.indexer = indexer

    def save_index(self, filepath):
        try:
            if filepath is None:
                raise ValueError("Filepath cannot be None")
            if not isinstance(filepath, str):
                raise ValueError(f"Filepath must be string, got {type(filepath).__name__}")
            if not filepath.strip():
                raise ValueError("Filepath cannot be empty string")
            if not self.indexer.index:
                raise ValueError("Index is empty, nothing to save")

            with open(filepath, "w") as f:
                json.dump(dict(self.indexer.index), f, indent=2)

            with open(filepath, "rb") as f:
                return len(f.read())

        except ValueError as e:
            raise e
        except (OSError, IOError) as e:
            raise OSError(f"Failed to write index to {filepath}: {e}")
        except Exception as e:
            raise OSError(f"Unexpected error saving index: {type(e).__name__}: {e}")

    def load_index(self, filepath):
        try:
            if filepath is None:
                raise ValueError("Filepath cannot be None")
            if not isinstance(filepath, str):
                raise ValueError(f"Filepath must be string, got {type(filepath).__name__}")
            if not filepath.strip():
                raise ValueError("Filepath cannot be empty string")
            if not Path(filepath).exists():
                raise FileNotFoundError(f"Index file not found: {filepath}")

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
        try:
            if filepath is None:
                raise ValueError("Filepath cannot be None")
            if not isinstance(filepath, str):
                raise ValueError(f"Filepath must be string, got {type(filepath).__name__}")
            if not filepath.strip():
                raise ValueError("Filepath cannot be empty string")
            if not self.indexer.documents:
                raise ValueError("Documents are empty, nothing to save")

            urls = getattr(self.indexer, "urls", {})
            if not isinstance(urls, dict):
                urls = {}
            data = {}
            for k, v in self.indexer.documents.items():
                entry = {"text": v}
                url = urls.get(k)
                if url is not None:
                    entry["url"] = url
                data[str(k)] = entry

            with open(filepath, "w") as f:
                json.dump(data, f, indent=2)

            with open(filepath, "rb") as f:
                return len(f.read())

        except ValueError as e:
            raise e
        except (OSError, IOError) as e:
            raise OSError(f"Failed to write documents to {filepath}: {e}")
        except Exception as e:
            raise OSError(f"Unexpected error saving documents: {type(e).__name__}: {e}")

    def load_documents(self, filepath):
        try:
            if filepath is None:
                raise ValueError("Filepath cannot be None")
            if not isinstance(filepath, str):
                raise ValueError(f"Filepath must be string, got {type(filepath).__name__}")
            if not filepath.strip():
                raise ValueError("Filepath cannot be empty string")
            if not Path(filepath).exists():
                raise FileNotFoundError(f"Documents file not found: {filepath}")

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
        try:
            if dirpath is None:
                raise ValueError("Directory path cannot be None")
            if not isinstance(dirpath, str):
                raise ValueError(f"Directory path must be string, got {type(dirpath).__name__}")
            if not dirpath.strip():
                raise ValueError("Directory path cannot be empty string")

            checkpoint_dir = Path(dirpath)
            checkpoint_dir.mkdir(parents=True, exist_ok=True)

            index_bytes = self.save_index(str(checkpoint_dir / "index.json"))
            docs_bytes = self.save_documents(str(checkpoint_dir / "documents.json"))
            return {"index_file": index_bytes, "docs_file": docs_bytes}

        except ValueError as e:
            raise e
        except (OSError, IOError) as e:
            raise OSError(f"Failed to create checkpoint at {dirpath}: {e}")
        except Exception as e:
            raise OSError(f"Error saving checkpoint: {type(e).__name__}: {e}")

    def load_checkpoint(self, dirpath):
        try:
            if dirpath is None:
                raise ValueError("Directory path cannot be None")
            if not isinstance(dirpath, str):
                raise ValueError(f"Directory path must be string, got {type(dirpath).__name__}")
            if not dirpath.strip():
                raise ValueError("Directory path cannot be empty string")

            checkpoint_dir = Path(dirpath)
            if not checkpoint_dir.exists():
                raise FileNotFoundError(f"Checkpoint directory not found: {dirpath}")

            index_file = checkpoint_dir / "index.json"
            docs_file = checkpoint_dir / "documents.json"
            if not index_file.exists():
                raise FileNotFoundError(f"Index file not found in checkpoint: {index_file}")
            if not docs_file.exists():
                raise FileNotFoundError(f"Documents file not found in checkpoint: {docs_file}")

            return {
                "index": self.load_index(str(index_file)),
                "documents": self.load_documents(str(docs_file)),
            }

        except (ValueError, FileNotFoundError, json.JSONDecodeError) as e:
            raise e
        except Exception as e:
            raise Exception(f"Error loading checkpoint: {type(e).__name__}: {e}")
