"""
Comprehensive tests for Persistence class.

Tests cover:
- Index save/load to JSON
- Documents save/load to JSON
- Checkpoint save/load (combined)
- File validation and error handling
- Data integrity checks
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
from src.persistence import Persistence


class TestPersistenceInit:
    """Tests for Persistence initialization."""

    def test_init_with_valid_indexer(self):
        """Persistence initializes with valid indexer."""
        indexer = Mock()
        persistence = Persistence(indexer)
        
        assert persistence.indexer == indexer

    def test_init_raises_error_if_indexer_none(self):
        """Persistence raises ValueError if indexer is None."""
        with pytest.raises(ValueError):
            Persistence(None)


class TestSaveIndex:
    """Tests for saving index to file."""

    @pytest.fixture
    def persistence_setup(self):
        """Provide persistence with mock indexer."""
        indexer = Mock()
        indexer.index = {"love": [1, 2], "search": [3]}
        indexer.documents = {1: "text1", 2: "text2", 3: "text3"}
        return Persistence(indexer)

    def test_save_index_creates_json_file(self, persistence_setup):
        """save_index creates JSON file with index data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = f"{tmpdir}/index.json"
            
            byte_count = persistence_setup.save_index(filepath)
            
            assert Path(filepath).exists()
            assert byte_count > 0
            
            with open(filepath) as f:
                data = json.load(f)
            assert "love" in data
            assert "search" in data

    def test_save_index_raises_error_if_filepath_none(self, persistence_setup):
        """save_index raises ValueError if filepath is None."""
        with pytest.raises(ValueError):
            persistence_setup.save_index(None)

    def test_save_index_raises_error_if_filepath_empty(self, persistence_setup):
        """save_index raises ValueError if filepath is empty."""
        with pytest.raises(ValueError):
            persistence_setup.save_index("")

    def test_save_index_raises_error_if_index_empty(self):
        """save_index raises ValueError if index is empty."""
        indexer = Mock()
        indexer.index = {}  # Empty index
        persistence = Persistence(indexer)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.raises(ValueError):
                persistence.save_index(f"{tmpdir}/index.json")

    def test_save_index_handles_file_permission_error(self, persistence_setup):
        """save_index propagates file permission errors."""
        with patch("builtins.open", side_effect=PermissionError("No permission")):
            with pytest.raises(OSError):
                persistence_setup.save_index("/protected/path/index.json")


class TestLoadIndex:
    """Tests for loading index from file."""

    @pytest.fixture
    def index_file(self):
        """Create a temporary index file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = f"{tmpdir}/index.json"
            data = {"love": [1, 2], "search": [3]}
            with open(filepath, "w") as f:
                json.dump(data, f)
            yield filepath

    def test_load_index_reads_json_file(self, index_file):
        """load_index reads and parses JSON file."""
        indexer = Mock()
        persistence = Persistence(indexer)
        
        data = persistence.load_index(index_file)
        
        assert data == {"love": [1, 2], "search": [3]}

    def test_load_index_raises_error_if_filepath_none(self):
        """load_index raises ValueError if filepath is None."""
        indexer = Mock()
        persistence = Persistence(indexer)
        
        with pytest.raises(ValueError):
            persistence.load_index(None)

    def test_load_index_raises_error_if_file_not_found(self):
        """load_index raises FileNotFoundError if file not found."""
        indexer = Mock()
        persistence = Persistence(indexer)
        
        with pytest.raises(FileNotFoundError):
            persistence.load_index("/nonexistent/path/index.json")

    def test_load_index_raises_error_if_json_invalid(self):
        """load_index raises JSONDecodeError if JSON malformed."""
        indexer = Mock()
        persistence = Persistence(indexer)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = f"{tmpdir}/bad.json"
            with open(filepath, "w") as f:
                f.write("{invalid json}")
            
            with pytest.raises(json.JSONDecodeError):
                persistence.load_index(filepath)


class TestSaveDocuments:
    """Tests for saving documents to file."""

    @pytest.fixture
    def persistence_setup(self):
        """Provide persistence with mock indexer."""
        indexer = Mock()
        indexer.index = {"word": [1]}
        indexer.documents = {1: "doc text 1", 2: "doc text 2"}
        return Persistence(indexer)

    def test_save_documents_creates_json_file(self, persistence_setup):
        """save_documents creates JSON file with documents."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = f"{tmpdir}/documents.json"
            
            byte_count = persistence_setup.save_documents(filepath)
            
            assert Path(filepath).exists()
            assert byte_count > 0
            
            with open(filepath) as f:
                data = json.load(f)
            # JSON converts int keys to strings
            assert "1" in data
            assert "2" in data

    def test_save_documents_raises_error_if_documents_empty(self):
        """save_documents raises ValueError if documents empty."""
        indexer = Mock()
        indexer.index = {"word": [1]}
        indexer.documents = {}  # Empty documents
        persistence = Persistence(indexer)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.raises(ValueError):
                persistence.save_documents(f"{tmpdir}/docs.json")

    def test_save_documents_raises_error_if_filepath_none(self, persistence_setup):
        """save_documents raises ValueError if filepath is None."""
        with pytest.raises(ValueError):
            persistence_setup.save_documents(None)


class TestLoadDocuments:
    """Tests for loading documents from file."""

    @pytest.fixture
    def documents_file(self):
        """Create a temporary documents file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = f"{tmpdir}/documents.json"
            data = {1: "doc text 1", 2: "doc text 2"}
            with open(filepath, "w") as f:
                json.dump(data, f)
            yield filepath

    def test_load_documents_reads_json_file(self, documents_file):
        """load_documents reads and parses JSON file."""
        indexer = Mock()
        persistence = Persistence(indexer)
        
        data = persistence.load_documents(documents_file)
        
        # JSON keys are strings, not integers
        assert data == {"1": "doc text 1", "2": "doc text 2"}

    def test_load_documents_raises_error_if_file_not_found(self):
        """load_documents raises FileNotFoundError if file not found."""
        indexer = Mock()
        persistence = Persistence(indexer)
        
        with pytest.raises(FileNotFoundError):
            persistence.load_documents("/nonexistent/path/documents.json")

    def test_load_documents_raises_error_if_json_invalid(self):
        """load_documents raises JSONDecodeError if JSON malformed."""
        indexer = Mock()
        persistence = Persistence(indexer)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = f"{tmpdir}/bad.json"
            with open(filepath, "w") as f:
                f.write("{bad json}")
            
            with pytest.raises(json.JSONDecodeError):
                persistence.load_documents(filepath)


class TestSaveCheckpoint:
    """Tests for checkpoint save (combined index + documents)."""

    @pytest.fixture
    def persistence_setup(self):
        """Provide persistence with mock indexer."""
        indexer = Mock()
        indexer.index = {"word": [1, 2]}
        indexer.documents = {1: "text1", 2: "text2"}
        return Persistence(indexer)

    def test_save_checkpoint_creates_directory_with_files(self, persistence_setup):
        """save_checkpoint creates directory with index + documents files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            checkpoint_dir = f"{tmpdir}/checkpoint"
            
            result = persistence_setup.save_checkpoint(checkpoint_dir)
            
            assert Path(checkpoint_dir).exists()
            assert "index_file" in result
            assert "docs_file" in result
            assert result["index_file"] > 0
            assert result["docs_file"] > 0

    def test_save_checkpoint_raises_error_if_dirpath_none(self, persistence_setup):
        """save_checkpoint raises ValueError if dirpath is None."""
        with pytest.raises(ValueError):
            persistence_setup.save_checkpoint(None)

    def test_save_checkpoint_files_are_valid_json(self, persistence_setup):
        """save_checkpoint creates valid JSON files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            checkpoint_dir = f"{tmpdir}/checkpoint"
            
            persistence_setup.save_checkpoint(checkpoint_dir)
            
            # Verify files are valid JSON
            index_file = Path(checkpoint_dir) / "index.json"
            docs_file = Path(checkpoint_dir) / "documents.json"
            
            with open(index_file) as f:
                json.load(f)  # Should not raise
            with open(docs_file) as f:
                json.load(f)  # Should not raise


class TestLoadCheckpoint:
    """Tests for checkpoint load (combined index + documents)."""

    @pytest.fixture
    def checkpoint_dir(self):
        """Create a temporary checkpoint directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            checkpoint_path = Path(tmpdir) / "checkpoint"
            checkpoint_path.mkdir()
            
            # Create index file
            with open(checkpoint_path / "index.json", "w") as f:
                json.dump({"word": [1, 2]}, f)
            
            # Create documents file
            with open(checkpoint_path / "documents.json", "w") as f:
                json.dump({1: "text1", 2: "text2"}, f)
            
            yield str(checkpoint_path)

    def test_load_checkpoint_loads_both_files(self, checkpoint_dir):
        """load_checkpoint loads index and documents."""
        indexer = Mock()
        persistence = Persistence(indexer)
        
        result = persistence.load_checkpoint(checkpoint_dir)
        
        assert "index" in result
        assert "documents" in result
        assert result["index"] == {"word": [1, 2]}
        assert result["documents"] == {1: "text1", 2: "text2"}

    def test_load_checkpoint_raises_error_if_dirpath_none(self):
        """load_checkpoint raises ValueError if dirpath is None."""
        indexer = Mock()
        persistence = Persistence(indexer)
        
        with pytest.raises(ValueError):
            persistence.load_checkpoint(None)

    def test_load_checkpoint_raises_error_if_directory_not_found(self):
        """load_checkpoint raises FileNotFoundError if directory not found."""
        indexer = Mock()
        persistence = Persistence(indexer)
        
        with pytest.raises(FileNotFoundError):
            persistence.load_checkpoint("/nonexistent/checkpoint")

    def test_load_checkpoint_raises_error_if_files_missing(self):
        """load_checkpoint raises FileNotFoundError if checkpoint files missing."""
        indexer = Mock()
        persistence = Persistence(indexer)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            checkpoint_dir = Path(tmpdir) / "checkpoint"
            checkpoint_dir.mkdir()
            # Create empty checkpoint directory (no files)
            
            with pytest.raises(FileNotFoundError):
                persistence.load_checkpoint(str(checkpoint_dir))


class TestPersistenceIntegration:
    """Integration tests for full save/load workflow."""

    def test_full_save_and_load_workflow(self):
        """Full workflow: save index + docs, then load them back."""
        indexer = Mock()
        indexer.index = {"love": [1, 2, 3], "life": [2]}
        indexer.documents = {1: "Love is important", 2: "Love life all day", 3: "Life happens"}
        
        persistence = Persistence(indexer)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            checkpoint_dir = f"{tmpdir}/checkpoint"
            
            # Save
            save_result = persistence.save_checkpoint(checkpoint_dir)
            assert save_result["index_file"] > 0
            assert save_result["docs_file"] > 0
            
            # Load
            load_result = persistence.load_checkpoint(checkpoint_dir)
            
            # Verify data integrity
            assert load_result["index"] == indexer.index
            assert load_result["documents"] == indexer.documents

    def test_save_and_load_preserves_data_types(self):
        """Save/load preserves data types (int keys -> string keys in JSON)."""
        indexer = Mock()
        indexer.index = {"word": [1, 2, 3]}
        indexer.documents = {1: "text1", 2: "text2"}
        
        persistence = Persistence(indexer)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            checkpoint_dir = f"{tmpdir}/checkpoint"
            persistence.save_checkpoint(checkpoint_dir)
            result = persistence.load_checkpoint(checkpoint_dir)
            
            # Note: JSON converts integer keys to strings
            # This is expected behavior to verify
            assert "word" in result["index"]
            assert isinstance(result["index"]["word"], list)
