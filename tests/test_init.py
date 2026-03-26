"""
Tests for instaparser package __init__.py exports.
"""

import instaparser


class TestInstaparserPackageExports:
    """Tests for package-level exports."""

    def test_instaparser_client_exported(self):
        """Test that InstaparserClient is exported."""
        assert hasattr(instaparser, "InstaparserClient")
        from instaparser import InstaparserClient

        assert InstaparserClient is instaparser.InstaparserClient

    def test_article_exported(self):
        """Test that Article is exported."""
        assert hasattr(instaparser, "Article")
        from instaparser import Article

        assert Article is instaparser.Article

    def test_pdf_exported(self):
        """Test that PDF is exported."""
        assert hasattr(instaparser, "PDF")
        from instaparser import PDF

        assert PDF is instaparser.PDF

    def test_summary_exported(self):
        """Test that Summary is exported."""
        assert hasattr(instaparser, "Summary")
        from instaparser import Summary

        assert Summary is instaparser.Summary

    def test_exceptions_exported(self):
        """Test that all exception classes are exported."""
        from instaparser import (
            InstaparserAPIError,
            InstaparserAuthenticationError,
            InstaparserError,
            InstaparserRateLimitError,
            InstaparserValidationError,
        )

        assert hasattr(instaparser, "InstaparserError")
        assert hasattr(instaparser, "InstaparserAPIError")
        assert hasattr(instaparser, "InstaparserAuthenticationError")
        assert hasattr(instaparser, "InstaparserRateLimitError")
        assert hasattr(instaparser, "InstaparserValidationError")

        assert InstaparserError is instaparser.InstaparserError
        assert InstaparserAPIError is instaparser.InstaparserAPIError
        assert InstaparserAuthenticationError is instaparser.InstaparserAuthenticationError
        assert InstaparserRateLimitError is instaparser.InstaparserRateLimitError
        assert InstaparserValidationError is instaparser.InstaparserValidationError

    def test_all_exports_match_all_list(self):
        """Test that __all__ list matches actual exports."""
        expected_exports = [
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

        assert hasattr(instaparser, "__all__")
        assert set(instaparser.__all__) == set(expected_exports)

        # Verify all items in __all__ are actually exported
        for item in instaparser.__all__:
            assert hasattr(instaparser, item), f"{item} is in __all__ but not exported"

    def test_version_exported(self):
        """Test that __version__ is exported."""
        assert hasattr(instaparser, "__version__")
        assert isinstance(instaparser.__version__, str)
        assert len(instaparser.__version__) > 0

    def test_import_from_instaparser(self):
        """Test that all classes can be imported from instaparser."""
        from instaparser import (
            PDF,
            Article,
            InstaparserAPIError,
            InstaparserAuthenticationError,
            InstaparserClient,
            InstaparserError,
            InstaparserRateLimitError,
            InstaparserValidationError,
            Summary,
        )

        # Verify they are classes
        assert isinstance(InstaparserClient, type)
        assert isinstance(Article, type)
        assert isinstance(PDF, type)
        assert isinstance(Summary, type)
        assert isinstance(InstaparserError, type)
        assert isinstance(InstaparserAPIError, type)
        assert isinstance(InstaparserAuthenticationError, type)
        assert isinstance(InstaparserRateLimitError, type)
        assert isinstance(InstaparserValidationError, type)

    def test_exception_inheritance_chain(self):
        """Test that exception inheritance chain is correct."""
        from instaparser import (
            InstaparserAPIError,
            InstaparserAuthenticationError,
            InstaparserError,
            InstaparserRateLimitError,
            InstaparserValidationError,
        )

        # Base exception
        assert issubclass(InstaparserError, Exception)

        # API errors inherit from base
        assert issubclass(InstaparserAPIError, InstaparserError)

        # Specific errors inherit from API error
        assert issubclass(InstaparserAuthenticationError, InstaparserAPIError)
        assert issubclass(InstaparserRateLimitError, InstaparserAPIError)
        assert issubclass(InstaparserValidationError, InstaparserAPIError)
