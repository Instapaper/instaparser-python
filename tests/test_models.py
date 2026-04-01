"""
Tests for model classes.
"""

from instaparser.models import PDF, Article, Summary


class TestArticle:
    """Tests for Article class."""

    def test_body_prefers_html_over_text(self):
        """Test that body prefers html over text."""
        article = Article(html="<p>HTML</p>", text="Text")
        assert article.body == "<p>HTML</p>"

    def test_body_prefers_html_over_markdown(self):
        """Test that body prefers html over markdown."""
        article = Article(html="<p>HTML</p>", markdown="# Markdown")
        assert article.body == "<p>HTML</p>"

    def test_body_prefers_text_over_markdown(self):
        """Test that body prefers text over markdown."""
        article = Article(text="Text", markdown="# Markdown")
        assert article.body == "Text"

    def test_body_falls_back_to_text(self):
        """Test that body falls back to text when html is missing."""
        article = Article(text="Text")
        assert article.body == "Text"

    def test_body_falls_back_to_markdown(self):
        """Test that body falls back to markdown when html and text are missing."""
        article = Article(markdown="# Markdown")
        assert article.body == "# Markdown"

    def test_body_is_none_when_all_missing(self):
        """Test that body is None when html, text, and markdown are all missing."""
        article = Article(url="https://example.com")
        assert article.body is None

    def test_body_treats_empty_string_as_falsy(self):
        """Test that body treats empty string html as falsy and falls through."""
        article = Article(html="", text="Text")
        assert article.body == "Text"

    def test_repr(self):
        """Test __repr__ includes class name, url, and title."""
        article = Article(url="https://example.com", title="Test")
        repr_str = repr(article)
        assert "Article" in repr_str
        assert "https://example.com" in repr_str
        assert "Test" in repr_str

    def test_str_returns_body(self):
        """Test __str__ returns body content."""
        article = Article(html="<p>Body</p>")
        assert str(article) == "<p>Body</p>"

    def test_str_returns_empty_when_no_body(self):
        """Test __str__ returns empty string when body is None."""
        article = Article()
        assert str(article) == ""


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


class TestSummary:
    """Tests for Summary class."""

    def test_repr_truncates_long_overview(self):
        """Test __repr__ truncates overview longer than 50 characters."""
        summary = Summary(
            key_sentences=["Sentence 1", "Sentence 2"],
            overview="This is a test overview that is longer than 50 characters for truncation",
        )
        repr_str = repr(summary)
        assert "..." in repr_str
        assert "key_sentences=2" in repr_str

    def test_repr_does_not_truncate_short_overview(self):
        """Test __repr__ does not add ellipsis for short overview."""
        summary = Summary(key_sentences=["Sentence"], overview="Short")
        repr_str = repr(summary)
        assert "..." not in repr_str
        assert "key_sentences=1" in repr_str

    def test_str_returns_overview(self):
        """Test __str__ returns the overview."""
        summary = Summary(key_sentences=["Sentence"], overview="The overview")
        assert str(summary) == "The overview"
