"""
Exception classes for the Instaparser Library.
"""

from typing import Any


class InstaparserError(Exception):
    """Base exception for all Instaparser errors."""


class InstaparserAPIError(InstaparserError):
    """Exception raised for API errors."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response: Any | None = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class InstaparserAuthenticationError(InstaparserAPIError):
    """Exception raised for authentication errors (401)."""


class InstaparserRateLimitError(InstaparserAPIError):
    """Exception raised for rate limit errors (429)."""


class InstaparserValidationError(InstaparserAPIError):
    """Exception raised for validation errors (400)."""
