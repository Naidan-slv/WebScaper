"""
Shared pytest fixtures for all tests.
"""

import pytest
from unittest.mock import Mock


@pytest.fixture
def mock_html_response():
    """Mock HTML response with sample quote content."""
    mock = Mock()
    mock.status_code = 200
    mock.text = """
    <html>
        <body>
            <p>The only way to do great work is to love what you do.</p>
        </body>
    </html>
    """
    return mock
