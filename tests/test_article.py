"""
Tests for Article class.
"""

import pytest
from instaparser.article import Article


class TestArticle:
    """Tests for Article class."""
    
    def test_article_initialization_with_full_data(self):
        """Test Article initialization with complete data."""
        data = {
            "url": "https://example.com/article",
            "title": "Test Article",
            "site_name": "Example Site",
            "author": "John Doe",
            "date": 1609459200,
            "description": "Test description",
            "thumbnail": "https://example.com/thumb.jpg",
            "words": 500,
            "is_rtl": False,
            "images": ["https://example.com/img1.jpg"],
            "videos": ["https://example.com/video1.mp4"],
            "html": "<p>Article body</p>",
        }
        article = Article(data)
        
        assert article.url == "https://example.com/article"
        assert article.title == "Test Article"
        assert article.site_name == "Example Site"
        assert article.author == "John Doe"
        assert article.date == 1609459200
        assert article.description == "Test description"
        assert article.thumbnail == "https://example.com/thumb.jpg"
        assert article.words == 500
        assert article.is_rtl is False
        assert article.images == ["https://example.com/img1.jpg"]
        assert article.videos == ["https://example.com/video1.mp4"]
        assert article.html == "<p>Article body</p>"
        assert article.body == "<p>Article body</p>"
    
    def test_article_initialization_with_text_output(self):
        """Test Article initialization with text output."""
        data = {
            "url": "https://example.com/article",
            "title": "Test Article",
            "text": "Article body in plain text",
        }
        article = Article(data)
        
        assert article.text == "Article body in plain text"
        assert article.html is None
        assert article.markdown is None
        assert article.body == "Article body in plain text"
    
    def test_article_initialization_with_markdown_output(self):
        """Test Article initialization with markdown output."""
        data = {
            "url": "https://example.com/article",
            "title": "Test Article",
            "markdown": "# Test Article\n\nArticle body in **markdown**",
        }
        article = Article(data)
        
        assert article.markdown == "# Test Article\n\nArticle body in **markdown**"
        assert article.html is None
        assert article.text is None
        assert article.body == "# Test Article\n\nArticle body in **markdown**"
    
    def test_article_initialization_with_minimal_data(self):
        """Test Article initialization with minimal data."""
        data = {"url": "https://example.com/article"}
        article = Article(data)
        
        assert article.url == "https://example.com/article"
        assert article.title is None
        assert article.author is None
        assert article.words == 0
        assert article.is_rtl is False
        assert article.images == []
        assert article.videos == []
        assert article.markdown is None
        assert article.body is None
    
    def test_article_initialization_prefers_html_over_text(self):
        """Test that Article prefers html over text for body."""
        data = {
            "url": "https://example.com/article",
            "html": "<p>HTML content</p>",
            "text": "Text content",
        }
        article = Article(data)
        
        assert article.html == "<p>HTML content</p>"
        assert article.text == "Text content"
        assert article.body == "<p>HTML content</p>"  # HTML takes precedence
    
    def test_article_body_precedence_html_over_markdown(self):
        """Test that Article prefers html over markdown for body."""
        data = {
            "url": "https://example.com/article",
            "html": "<p>HTML content</p>",
            "markdown": "# Markdown content",
        }
        article = Article(data)
        
        assert article.body == "<p>HTML content</p>"
    
    def test_article_body_precedence_text_over_markdown(self):
        """Test that Article prefers text over markdown for body."""
        data = {
            "url": "https://example.com/article",
            "text": "Text content",
            "markdown": "# Markdown content",
        }
        article = Article(data)
        
        assert article.body == "Text content"
    
    def test_article_initialization_with_rtl(self):
        """Test Article initialization with RTL language."""
        data = {
            "url": "https://example.com/article",
            "is_rtl": True,
        }
        article = Article(data)
        
        assert article.is_rtl is True
    
    def test_article_repr(self):
        """Test Article __repr__ method."""
        data = {
            "url": "https://example.com/article",
            "title": "Test Article",
        }
        article = Article(data)
        
        repr_str = repr(article)
        assert "Article" in repr_str
        assert "https://example.com/article" in repr_str
        assert "Test Article" in repr_str
    
    def test_article_str(self):
        """Test Article __str__ method."""
        data = {
            "url": "https://example.com/article",
            "html": "<p>Article body</p>",
        }
        article = Article(data)
        
        assert str(article) == "<p>Article body</p>"
    
    def test_article_str_with_no_body(self):
        """Test Article __str__ method when body is None."""
        data = {"url": "https://example.com/article"}
        article = Article(data)
        
        assert str(article) == ""
    
    def test_article_with_empty_images_and_videos(self):
        """Test Article with empty images and videos lists."""
        data = {
            "url": "https://example.com/article",
            "images": [],
            "videos": [],
        }
        article = Article(data)
        
        assert article.images == []
        assert article.videos == []
    
    def test_article_with_multiple_images(self):
        """Test Article with multiple images."""
        data = {
            "url": "https://example.com/article",
            "images": [
                "https://example.com/img1.jpg",
                "https://example.com/img2.jpg",
                "https://example.com/img3.jpg",
            ],
        }
        article = Article(data)
        
        assert len(article.images) == 3
        assert article.images[0] == "https://example.com/img1.jpg"
    
    def test_article_with_none_values(self):
        """Test Article handles None values gracefully."""
        data = {
            "url": "https://example.com/article",
            "title": None,
            "author": None,
            "description": None,
            "thumbnail": None,
        }
        article = Article(data)
        
        assert article.title is None
        assert article.author is None
        assert article.description is None
        assert article.thumbnail is None
    
    def test_article_with_zero_words(self):
        """Test Article with zero words."""
        data = {
            "url": "https://example.com/article",
            "words": 0,
        }
        article = Article(data)
        
        assert article.words == 0
    
    def test_article_with_negative_words(self):
        """Test Article handles negative words (edge case)."""
        data = {
            "url": "https://example.com/article",
            "words": -1,
        }
        article = Article(data)
        
        assert article.words == -1
    
    def test_article_with_very_large_word_count(self):
        """Test Article with very large word count."""
        data = {
            "url": "https://example.com/article",
            "words": 999999,
        }
        article = Article(data)
        
        assert article.words == 999999
    
    def test_article_with_empty_string_values(self):
        """Test Article with empty string values."""
        data = {
            "url": "https://example.com/article",
            "title": "",
            "author": "",
            "description": "",
            "html": "",
        }
        article = Article(data)
        
        assert article.title == ""
        assert article.author == ""
        assert article.description == ""
        assert article.html == ""
        assert article.body is None
    
    def test_article_with_unicode_content(self):
        """Test Article with Unicode content."""
        data = {
            "url": "https://example.com/article",
            "title": "测试文章标题",
            "author": "作者名",
            "html": "<p>这是文章内容。包含中文、日本語、한국어。</p>",
        }
        article = Article(data)
        
        assert article.title == "测试文章标题"
        assert article.author == "作者名"
        assert "中文" in article.html
        assert "日本語" in article.html
        assert "한국어" in article.html
    
    def test_article_with_special_characters_in_fields(self):
        """Test Article with special characters in fields."""
        data = {
            "url": "https://example.com/article",
            "title": "Article with 'quotes' & \"double quotes\"",
            "author": "Author <name> & Co.",
            "description": "Description with\nnewlines\tand\ttabs",
        }
        article = Article(data)
        
        assert "'quotes'" in article.title
        assert '"double quotes"' in article.title
        assert "<name>" in article.author
        assert "\n" in article.description
        assert "\t" in article.description
    
    def test_article_with_very_long_title(self):
        """Test Article with very long title."""
        long_title = "A" * 10000
        data = {
            "url": "https://example.com/article",
            "title": long_title,
        }
        article = Article(data)
        
        assert len(article.title) == 10000
        assert article.title == long_title
    
    def test_article_with_very_long_body(self):
        """Test Article with very long body."""
        long_body = "<p>" + "Content " * 100000 + "</p>"
        data = {
            "url": "https://example.com/article",
            "html": long_body,
        }
        article = Article(data)
        
        assert len(article.html) > 100000
        assert article.body == long_body
    
    def test_article_date_as_string(self):
        """Test Article handles date as string (edge case)."""
        data = {
            "url": "https://example.com/article",
            "date": "2021-01-01",
        }
        article = Article(data)
        
        # Should accept string date
        assert article.date == "2021-01-01"
    
    def test_article_date_as_none(self):
        """Test Article with None date."""
        data = {
            "url": "https://example.com/article",
            "date": None,
        }
        article = Article(data)
        
        assert article.date is None
    
    def test_article_with_complex_html(self):
        """Test Article with complex HTML structure."""
        complex_html = """
        <article>
            <header>
                <h1>Title</h1>
                <div class="meta">Meta info</div>
            </header>
            <div class="content">
                <p>Paragraph 1</p>
                <p>Paragraph 2</p>
                <img src="image.jpg" alt="Image">
                <iframe src="video.mp4"></iframe>
            </div>
        </article>
        """
        data = {
            "url": "https://example.com/article",
            "html": complex_html,
        }
        article = Article(data)
        
        assert "<article>" in article.html
        assert "<h1>Title</h1>" in article.html
        assert "<img" in article.html
    
    def test_article_body_fallback_to_text_when_html_missing(self):
        """Test Article body falls back to text when html is missing."""
        data = {
            "url": "https://example.com/article",
            "text": "Plain text content",
        }
        article = Article(data)
        
        assert article.html is None
        assert article.text == "Plain text content"
        assert article.body == "Plain text content"
    
    def test_article_body_fallback_to_markdown_when_html_and_text_missing(self):
        """Test Article body falls back to markdown when html and text are missing."""
        data = {
            "url": "https://example.com/article",
            "markdown": "# Markdown content",
        }
        article = Article(data)
        
        assert article.html is None
        assert article.text is None
        assert article.markdown == "# Markdown content"
        assert article.body == "# Markdown content"
    
    def test_article_body_none_when_all_missing(self):
        """Test Article body is None when html, text, and markdown are all missing."""
        data = {
            "url": "https://example.com/article",
        }
        article = Article(data)
        
        assert article.html is None
        assert article.text is None
        assert article.markdown is None
        assert article.body is None
