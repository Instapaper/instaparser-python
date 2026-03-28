"""
Tests for Article class.
"""

from instaparser.article import Article


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
