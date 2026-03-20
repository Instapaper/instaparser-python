"""
Instaparser Python Library

A Python client library for the Instaparser API.
"""

from .client import InstaparserClient
from .article import Article
from .pdf import PDF
from .summary import Summary
from .exceptions import (
    InstaparserError,
    InstaparserAPIError,
    InstaparserAuthenticationError,
    InstaparserRateLimitError,
    InstaparserValidationError,
)

__version__ = "1.0.1"

__all__ = [
    "InstaparserClient",
    "Article",
    "PDF",
    "Summary",
    "InstaparserError",
    "InstaparserAPIError",
    "InstaparserAuthenticationError",
    "InstaparserRateLimitError",
    "InstaparserValidationError",
]
