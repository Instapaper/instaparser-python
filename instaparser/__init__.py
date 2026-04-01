"""
Instaparser Python Library

A Python client library for the Instaparser API.
"""

from .client import InstaparserClient
from .exceptions import (
    InstaparserAPIError,
    InstaparserAuthenticationError,
    InstaparserError,
    InstaparserRateLimitError,
    InstaparserValidationError,
)
from .models import PDF, Article, Summary

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
