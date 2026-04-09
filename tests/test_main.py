"""
Tests for main entry point.
"""

from unittest.mock import patch, MagicMock
from src.main import main


class TestMain:
    """Tests for main() entry point."""

    @patch("src.main.CLI")
    def test_main_creates_cli_and_runs(self, mock_cli_cls):
        """main() creates a CLI instance and calls run()."""
        mock_cli = MagicMock()
        mock_cli_cls.return_value = mock_cli

        main()

        mock_cli_cls.assert_called_once()
        mock_cli.run.assert_called_once()
