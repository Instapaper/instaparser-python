"""
Shared fixtures and utilities for tests.
"""

import json
from unittest.mock import Mock, MagicMock
import pytest
import requests
from instaparser import InstaparserClient


@pytest.fixture
def api_key():
    """Sample API key for testing."""
    return "test-api-key-12345"


@pytest.fixture
def base_url():
    """Base URL for testing."""
    return "https://api.test.instaparser.com"


@pytest.fixture
def client(api_key, base_url):
    """Create an InstaparserClient instance for testing."""
    return InstaparserClient(api_key=api_key, base_url=base_url)


@pytest.fixture
def mock_article_response():
    """Mock article API response."""
    return {
        "url": "https://example.com/article",
        "title": "Test Article Title",
        "site_name": "Example Site",
        "author": "John Doe",
        "date": 1609459200,
        "description": "This is a test article description",
        "thumbnail": "https://example.com/thumb.jpg",
        "words": 500,
        "is_rtl": False,
        "images": ["https://example.com/image1.jpg"],
        "videos": [],
        "html": "<p>This is the article body in HTML format.</p>",
    }


@pytest.fixture
def mock_article_text_response():
    """Mock article API response with text output."""
    return {
        "url": "https://example.com/article",
        "title": "Test Article Title",
        "site_name": "Example Site",
        "author": "John Doe",
        "date": 1609459200,
        "description": "This is a test article description",
        "thumbnail": "https://example.com/thumb.jpg",
        "words": 500,
        "is_rtl": False,
        "images": ["https://example.com/image1.jpg"],
        "videos": [],
        "text": "This is the article body in plain text format.",
    }


@pytest.fixture
def mock_article_markdown_response():
    """Mock article API response with markdown output."""
    return {
        "url": "https://example.com/article",
        "title": "Test Article Title",
        "site_name": "Example Site",
        "author": "John Doe",
        "date": 1609459200,
        "description": "This is a test article description",
        "thumbnail": "https://example.com/thumb.jpg",
        "words": 500,
        "is_rtl": False,
        "images": ["https://example.com/image1.jpg"],
        "videos": [],
        "markdown": "# Test Article Title\n\nThis is the article body in **markdown** format.",
    }


@pytest.fixture
def mock_summary_response():
    """Mock summary API response."""
    return {
        "key_sentences": [
            "This is the first key sentence.",
            "This is the second key sentence.",
            "This is the third key sentence.",
        ],
        "overview": "This is a comprehensive overview of the article content.",
    }


@pytest.fixture
def mock_pdf_response():
    """Mock PDF API response."""
    return {
        "url": "https://example.com/document.pdf",
        "title": "Test PDF Document",
        "site_name": "Example Site",
        "author": "Jane Smith",
        "date": 1609459200,
        "description": "This is a test PDF document",
        "thumbnail": None,
        "words": 1000,
        "is_rtl": False,
        "images": [],
        "videos": [],
        "html": "<p>This is the PDF content in HTML format.</p>",
    }


@pytest.fixture
def mock_response():
    """Create a mock requests.Response object."""
    def _create_response(status_code=200, json_data=None, text=None, headers=None):
        response = Mock(spec=requests.Response)
        response.status_code = status_code
        response.headers = headers or {"Content-Type": "application/json"}
        
        if json_data is not None:
            response.json.return_value = json_data
            response.text = json.dumps(json_data)
        elif text is not None:
            response.text = text
            response.json.side_effect = ValueError("Not JSON")
        else:
            response.json.return_value = {}
            response.text = ""
        
        return response
    return _create_response


@pytest.fixture
def mock_session(mocker):
    """Mock the requests.Session used by InstaparserClient."""
    session = MagicMock(spec=requests.Session)
    session.headers = {}
    session.post = MagicMock()
    session.get = MagicMock()
    
    # Default successful response
    default_response = Mock(spec=requests.Response)
    default_response.status_code = 200
    default_response.json.return_value = {}
    default_response.text = "{}"
    default_response.headers = {}
    session.post.return_value = default_response
    session.get.return_value = default_response
    
    # Patch requests.Session to return our mock
    mocker.patch('requests.Session', return_value=session)
    return session
