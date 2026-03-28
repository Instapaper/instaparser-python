"""
Tests for PDF class.
"""

from instaparser.article import Article
from instaparser.pdf import PDF


class TestPDF:
    """Tests for PDF class."""

    def test_inherits_from_article(self):
        """Test that PDF inherits from Article."""
        assert issubclass(PDF, Article)

    def test_forces_is_rtl_false(self):
        """Test that PDF always sets is_rtl to False, even if True is passed."""
        pdf = PDF(is_rtl=True)
        assert pdf.is_rtl is False

    def test_forces_videos_empty(self):
        """Test that PDF always sets videos to [], even if videos are passed."""
        pdf = PDF(videos=["https://example.com/video.mp4"])
        assert pdf.videos == []

    def test_repr(self):
        """Test __repr__ includes class name, url, and title."""
        pdf = PDF(url="https://example.com/doc.pdf", title="Test PDF")
        repr_str = repr(pdf)
        assert "PDF" in repr_str
        assert "https://example.com/doc.pdf" in repr_str
        assert "Test PDF" in repr_str

    def test_str_returns_body(self):
        """Test that __str__ is inherited from Article and returns body."""
        pdf = PDF(html="<p>Content</p>")
        assert str(pdf) == "<p>Content</p>"
