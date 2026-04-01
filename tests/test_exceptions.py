"""
Tests for exception classes.
"""

from instaparser.exceptions import InstaparserAPIError


class TestInstaparserAPIError:
    """Tests for InstaparserAPIError attributes."""

    def test_message(self):
        error = InstaparserAPIError("API error occurred")
        assert str(error) == "API error occurred"
        assert error.status_code is None
        assert error.response is None

    def test_status_code(self):
        error = InstaparserAPIError("API error", status_code=500)
        assert error.status_code == 500

    def test_response(self):
        response = object()
        error = InstaparserAPIError("API error", status_code=500, response=response)
        assert error.response is response
