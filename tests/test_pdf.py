"""
Tests for PDF class.
"""

import pytest
from instaparser.pdf import PDF
from instaparser.article import Article


class TestPDF:
    """Tests for PDF class."""
    
    def test_pdf_inherits_from_article(self):
        """Test that PDF inherits from Article."""
        assert issubclass(PDF, Article)
    
    def test_pdf_initialization(self):
        """Test PDF initialization with data."""
        data = {
            "url": "https://example.com/document.pdf",
            "title": "Test PDF",
            "words": 1000,
            "html": "<p>PDF content</p>",
        }
        pdf = PDF(data)
        
        assert pdf.url == "https://example.com/document.pdf"
        assert pdf.title == "Test PDF"
        assert pdf.words == 1000
        assert pdf.html == "<p>PDF content</p>"
        assert pdf.is_rtl is False
        assert pdf.videos == []
    
    def test_pdf_always_has_is_rtl_false(self):
        """Test that PDF always sets is_rtl to False."""
        data = {
            "url": "https://example.com/document.pdf",
            "is_rtl": True,  # Even if data says True
        }
        pdf = PDF(data)
        
        assert pdf.is_rtl is False
    
    def test_pdf_always_has_empty_videos(self):
        """Test that PDF always has empty videos list."""
        data = {
            "url": "https://example.com/document.pdf",
            "videos": ["https://example.com/video.mp4"],  # Even if data has videos
        }
        pdf = PDF(data)
        
        assert pdf.videos == []
    
    def test_pdf_repr(self):
        """Test PDF __repr__ method."""
        data = {
            "url": "https://example.com/document.pdf",
            "title": "Test PDF",
        }
        pdf = PDF(data)
        
        repr_str = repr(pdf)
        assert "PDF" in repr_str
        assert "https://example.com/document.pdf" in repr_str
        assert "Test PDF" in repr_str
    
    def test_pdf_inherits_article_properties(self):
        """Test that PDF inherits all Article properties."""
        data = {
            "url": "https://example.com/document.pdf",
            "title": "Test PDF",
            "author": "Jane Smith",
            "words": 500,
            "html": "<p>Content</p>",
        }
        pdf = PDF(data)
        
        # All Article properties should be accessible
        assert pdf.url == "https://example.com/document.pdf"
        assert pdf.title == "Test PDF"
        assert pdf.author == "Jane Smith"
        assert pdf.words == 500
        assert pdf.html == "<p>Content</p>"
        assert pdf.body == "<p>Content</p>"
    
    def test_pdf_with_text_output(self):
        """Test PDF with text output format."""
        data = {
            "url": "https://example.com/document.pdf",
            "text": "PDF content in plain text",
        }
        pdf = PDF(data)
        
        assert pdf.text == "PDF content in plain text"
        assert pdf.body == "PDF content in plain text"
        assert pdf.is_rtl is False
        assert pdf.videos == []
    
    def test_pdf_with_markdown_output(self):
        """Test PDF with markdown output format."""
        data = {
            "url": "https://example.com/document.pdf",
            "markdown": "# PDF Title\n\nPDF content in **markdown**",
        }
        pdf = PDF(data)
        
        assert pdf.markdown == "# PDF Title\n\nPDF content in **markdown**"
        assert pdf.body == "# PDF Title\n\nPDF content in **markdown**"
        assert pdf.is_rtl is False
        assert pdf.videos == []
    
    def test_pdf_overrides_is_rtl_even_if_true_in_data(self):
        """Test that PDF always overrides is_rtl to False even if data has True."""
        data = {
            "url": "https://example.com/document.pdf",
            "is_rtl": True,
        }
        pdf = PDF(data)
        
        # Should be False regardless of input
        assert pdf.is_rtl is False
    
    def test_pdf_overrides_videos_even_if_present_in_data(self):
        """Test that PDF always overrides videos to [] even if data has videos."""
        data = {
            "url": "https://example.com/document.pdf",
            "videos": ["https://example.com/video1.mp4", "https://example.com/video2.mp4"],
        }
        pdf = PDF(data)
        
        # Should be empty list regardless of input
        assert pdf.videos == []
    
    def test_pdf_with_unicode_content(self):
        """Test PDF with Unicode content."""
        data = {
            "url": "https://example.com/document.pdf",
            "title": "测试PDF文档",
            "html": "<p>这是PDF内容。包含中文、日本語、한국어。</p>",
        }
        pdf = PDF(data)
        
        assert pdf.title == "测试PDF文档"
        assert "中文" in pdf.html
        assert pdf.is_rtl is False
        assert pdf.videos == []
    
    def test_pdf_with_special_characters(self):
        """Test PDF with special characters in fields."""
        data = {
            "url": "https://example.com/document.pdf",
            "title": "PDF with 'quotes' & \"double quotes\"",
            "author": "Author <name> & Co.",
        }
        pdf = PDF(data)
        
        assert "'quotes'" in pdf.title
        assert "<name>" in pdf.author
        assert pdf.is_rtl is False
        assert pdf.videos == []
    
    def test_pdf_with_very_long_content(self):
        """Test PDF with very long content."""
        long_html = "<p>" + "Content " * 100000 + "</p>"
        data = {
            "url": "https://example.com/document.pdf",
            "html": long_html,
        }
        pdf = PDF(data)
        
        assert len(pdf.html) > 100000
        assert pdf.is_rtl is False
        assert pdf.videos == []
    
    def test_pdf_with_none_values(self):
        """Test PDF handles None values gracefully."""
        data = {
            "url": "https://example.com/document.pdf",
            "title": None,
            "author": None,
            "description": None,
            "thumbnail": None,
        }
        pdf = PDF(data)
        
        assert pdf.title is None
        assert pdf.author is None
        assert pdf.description is None
        assert pdf.thumbnail is None
        assert pdf.is_rtl is False
        assert pdf.videos == []
    
    def test_pdf_with_empty_strings(self):
        """Test PDF with empty string values."""
        data = {
            "url": "https://example.com/document.pdf",
            "title": "",
            "author": "",
            "html": "",
        }
        pdf = PDF(data)
        
        assert pdf.title == ""
        assert pdf.author == ""
        assert pdf.html == ""
        assert pdf.body is None
        assert pdf.is_rtl is False
        assert pdf.videos == []
    
    def test_pdf_inherits_all_article_methods(self):
        """Test that PDF inherits all Article methods including __str__ and __repr__."""
        data = {
            "url": "https://example.com/document.pdf",
            "title": "Test PDF",
            "html": "<p>Content</p>",
        }
        pdf = PDF(data)
        
        # Should have Article's __str__ method
        assert str(pdf) == "<p>Content</p>"
        
        # Should have Article's __repr__ method (overridden)
        repr_str = repr(pdf)
        assert "PDF" in repr_str
        assert "Test PDF" in repr_str
    
    def test_pdf_with_zero_words(self):
        """Test PDF with zero words."""
        data = {
            "url": "https://example.com/document.pdf",
            "words": 0,
        }
        pdf = PDF(data)
        
        assert pdf.words == 0
        assert pdf.is_rtl is False
        assert pdf.videos == []
    
    def test_pdf_with_very_large_word_count(self):
        """Test PDF with very large word count."""
        data = {
            "url": "https://example.com/document.pdf",
            "words": 999999,
        }
        pdf = PDF(data)
        
        assert pdf.words == 999999
        assert pdf.is_rtl is False
        assert pdf.videos == []
    
    def test_pdf_with_complex_html(self):
        """Test PDF with complex HTML structure."""
        complex_html = """
        <div>
            <h1>PDF Title</h1>
            <p>Paragraph 1</p>
            <p>Paragraph 2</p>
            <img src="image.jpg">
        </div>
        """
        data = {
            "url": "https://example.com/document.pdf",
            "html": complex_html,
        }
        pdf = PDF(data)
        
        assert "<h1>PDF Title</h1>" in pdf.html
        assert "<img" in pdf.html
        assert pdf.is_rtl is False
        assert pdf.videos == []
