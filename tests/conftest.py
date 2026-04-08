"""
Shared pytest fixtures for all tests.
"""

import pytest
from unittest.mock import Mock, patch


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


@pytest.fixture(autouse=True)
def mock_time_sleep():
    """
    Auto-mock time.sleep for all tests to prevent actual delays.
    
    This allows tests to run quickly even though fetch_page calls time.sleep.
    Tests that specifically want to test timing can override this fixture.
    """
    with patch('src.crawler.time.sleep'):
        yield
