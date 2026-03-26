"""
Exception classes for the Instaparser Library.
"""


class InstaparserError(Exception):
    """Base exception for all Instaparser errors."""

    pass


class InstaparserAPIError(InstaparserError):
    """Exception raised for API errors."""

    def __init__(self, message, status_code=None, response=None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class InstaparserAuthenticationError(InstaparserAPIError):
    """Exception raised for authentication errors (401)."""

    pass


class InstaparserRateLimitError(InstaparserAPIError):
    """Exception raised for rate limit errors (429)."""

    pass


class InstaparserValidationError(InstaparserAPIError):
    """Exception raised for validation errors (400)."""

    pass
