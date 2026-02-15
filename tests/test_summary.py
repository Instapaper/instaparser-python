"""
Tests for Summary class.
"""

from instaparser.summary import Summary


class TestSummary:
    """Tests for Summary class."""

    def test_repr(self):
        """Test __repr__ includes class name, truncated overview, and sentence count."""
        summary = Summary(
            key_sentences=["Sentence 1", "Sentence 2"],
            overview="This is a test overview that is longer than 50 characters for truncation",
        )
        repr_str = repr(summary)
        assert "Summary" in repr_str
        assert "key_sentences=2" in repr_str

    def test_repr_with_short_overview(self):
        """Test __repr__ with short overview."""
        summary = Summary(key_sentences=["Sentence"], overview="Short")
        repr_str = repr(summary)
        assert "Summary" in repr_str
        assert "key_sentences=1" in repr_str

    def test_str_returns_overview(self):
        """Test __str__ returns the overview."""
        summary = Summary(key_sentences=["Sentence"], overview="The overview")
        assert str(summary) == "The overview"
