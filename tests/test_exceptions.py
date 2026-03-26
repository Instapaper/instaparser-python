"""
Tests for exception classes.
"""

import pytest

from instaparser.exceptions import (
    InstaparserAPIError,
    InstaparserAuthenticationError,
    InstaparserError,
    InstaparserRateLimitError,
    InstaparserValidationError,
)


class TestInstaparserError:
    """Tests for base InstaparserError exception."""

    def test_instaparser_error_is_exception(self):
        """Test that InstaparserError is an Exception."""
        assert issubclass(InstaparserError, Exception)

    def test_instaparser_error_can_be_raised(self):
        """Test that InstaparserError can be raised and caught."""
        with pytest.raises(InstaparserError):
            raise InstaparserError("Test error")


class TestInstaparserAPIError:
    """Tests for InstaparserAPIError exception."""

    def test_instaparser_api_error_inherits_from_base(self):
        """Test that InstaparserAPIError inherits from InstaparserError."""
        assert issubclass(InstaparserAPIError, InstaparserError)

    def test_instaparser_api_error_with_message(self):
        """Test InstaparserAPIError with just a message."""
        error = InstaparserAPIError("API error occurred")
        assert str(error) == "API error occurred"
        assert error.status_code is None
        assert error.response is None

    def test_instaparser_api_error_with_status_code(self):
        """Test InstaparserAPIError with status code."""
        error = InstaparserAPIError("API error", status_code=500)
        assert str(error) == "API error"
        assert error.status_code == 500
        assert error.response is None

    def test_instaparser_api_error_with_response(self):
        """Test InstaparserAPIError with response object."""
        mock_response = type("MockResponse", (), {"status_code": 500})()
        error = InstaparserAPIError("API error", status_code=500, response=mock_response)
        assert str(error) == "API error"
        assert error.status_code == 500
        assert error.response == mock_response


class TestInstaparserAuthenticationError:
    """Tests for InstaparserAuthenticationError exception."""

    def test_authentication_error_inherits_from_api_error(self):
        """Test that InstaparserAuthenticationError inherits from InstaparserAPIError."""
        assert issubclass(InstaparserAuthenticationError, InstaparserAPIError)

    def test_authentication_error_can_be_raised(self):
        """Test that InstaparserAuthenticationError can be raised."""
        with pytest.raises(InstaparserAuthenticationError):
            raise InstaparserAuthenticationError("Invalid API key", status_code=401)


class TestInstaparserRateLimitError:
    """Tests for InstaparserRateLimitError exception."""

    def test_rate_limit_error_inherits_from_api_error(self):
        """Test that InstaparserRateLimitError inherits from InstaparserAPIError."""
        assert issubclass(InstaparserRateLimitError, InstaparserAPIError)

    def test_rate_limit_error_can_be_raised(self):
        """Test that InstaparserRateLimitError can be raised."""
        with pytest.raises(InstaparserRateLimitError):
            raise InstaparserRateLimitError("Rate limit exceeded", status_code=429)


class TestInstaparserValidationError:
    """Tests for InstaparserValidationError exception."""

    def test_validation_error_inherits_from_api_error(self):
        """Test that InstaparserValidationError inherits from InstaparserAPIError."""
        assert issubclass(InstaparserValidationError, InstaparserAPIError)

    def test_validation_error_can_be_raised(self):
        """Test that InstaparserValidationError can be raised."""
        with pytest.raises(InstaparserValidationError):
            raise InstaparserValidationError("Invalid request", status_code=400)
