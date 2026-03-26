"""
Instaparser Python Library

A Python client library for the Instaparser API.
"""

from .article import Article
from .client import InstaparserClient
from .exceptions import (
    InstaparserAPIError,
    InstaparserAuthenticationError,
    InstaparserError,
    InstaparserRateLimitError,
    InstaparserValidationError,
)
from .pdf import PDF
from .summary import Summary

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
