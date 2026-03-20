"""
Integration-style tests for Instaparser Library.

These tests verify that the library components work together correctly,
though they still use mocking to avoid actual API calls.
"""

import json
from unittest.mock import Mock, patch
import pytest
import requests
from instaparser import InstaparserClient
from instaparser.exceptions import (
    InstaparserAPIError,
    InstaparserAuthenticationError,
    InstaparserRateLimitError,
    InstaparserValidationError,
)


class TestClientArticleIntegration:
    """Integration tests for Article functionality."""
    
    def test_full_article_workflow(self, api_key, base_url, mock_response):
        """Test complete article parsing workflow."""
        client = InstaparserClient(api_key=api_key, base_url=base_url)
        
        article_data = {
            "url": "https://example.com/article",
            "title": "Test Article",
            "author": "John Doe",
            "words": 500,
            "html": "<p>Article content</p>",
        }
        
        with patch.object(client.session, 'post') as mock_post:
            response = mock_response(status_code=200, json_data=article_data)
            mock_post.return_value = response
            
            article = client.Article(url="https://example.com/article")
            
            assert article.url == "https://example.com/article"
            assert article.title == "Test Article"
            assert article.author == "John Doe"
            assert article.words == 500
            assert article.body == "<p>Article content</p>"
    
    def test_article_with_error_handling(self, api_key, base_url, mock_response):
        """Test article parsing with error handling."""
        client = InstaparserClient(api_key=api_key, base_url=base_url)
        
        with patch.object(client.session, 'post') as mock_post:
            response = mock_response(status_code=401, json_data={"reason": "Invalid API key"})
            mock_post.return_value = response
            
            with pytest.raises(InstaparserAuthenticationError) as exc_info:
                client.Article(url="https://example.com/article")
            
            assert exc_info.value.status_code == 401
            assert "Invalid API key" in str(exc_info.value)


class TestClientSummaryIntegration:
    """Integration tests for Summary functionality."""
    
    def test_full_summary_workflow(self, api_key, base_url, mock_response):
        """Test complete summary generation workflow."""
        client = InstaparserClient(api_key=api_key, base_url=base_url)
        
        summary_data = {
            "key_sentences": ["Sentence 1", "Sentence 2"],
            "overview": "This is the overview",
        }
        
        with patch.object(client.session, 'post') as mock_post:
            response = mock_response(status_code=200, json_data=summary_data)
            mock_post.return_value = response
            
            summary = client.Summary(url="https://example.com/article")
            
            assert len(summary.key_sentences) == 2
            assert summary.overview == "This is the overview"
    
    def test_summary_streaming_workflow(self, api_key, base_url):
        """Test complete streaming summary workflow."""
        client = InstaparserClient(api_key=api_key, base_url=base_url)
        
        stream_lines = [
            b'key_sentences: ["Key 1", "Key 2"]',
            b'delta: Overview',
            b'delta:  text',
        ]
        
        with patch.object(client.session, 'post') as mock_post:
            streaming_response = Mock(spec=requests.Response)
            streaming_response.status_code = 200
            streaming_response.iter_lines.return_value = stream_lines
            streaming_response.headers = {}
            mock_post.return_value = streaming_response
            
            received = []
            def callback(line):
                received.append(line)
            
            summary = client.Summary(
                url="https://example.com/article",
                stream_callback=callback
            )
            
            assert len(received) == 3
            assert len(summary.key_sentences) == 2
            assert summary.overview == "Overview text"


class TestClientPDFIntegration:
    """Integration tests for PDF functionality."""
    
    def test_full_pdf_workflow_from_url(self, api_key, base_url, mock_response):
        """Test complete PDF parsing workflow from URL."""
        client = InstaparserClient(api_key=api_key, base_url=base_url)
        
        pdf_data = {
            "url": "https://example.com/document.pdf",
            "title": "Test PDF",
            "words": 1000,
            "html": "<p>PDF content</p>",
        }
        
        with patch.object(client.session, 'get') as mock_get:
            response = mock_response(status_code=200, json_data=pdf_data)
            mock_get.return_value = response
            
            pdf = client.PDF(url="https://example.com/document.pdf")
            
            assert pdf.url == "https://example.com/document.pdf"
            assert pdf.title == "Test PDF"
            assert pdf.words == 1000
            assert pdf.body == "<p>PDF content</p>"
            assert pdf.is_rtl is False
            assert pdf.videos == []
    
    def test_full_pdf_workflow_from_file(self, api_key, base_url, mock_response):
        """Test complete PDF parsing workflow from file."""
        client = InstaparserClient(api_key=api_key, base_url=base_url)
        
        pdf_data = {
            "url": "https://example.com/document.pdf",
            "title": "Test PDF",
            "words": 1000,
            "html": "<p>PDF content</p>",
        }
        
        pdf_file = b"PDF file content"
        
        with patch.object(client.session, 'post') as mock_post:
            response = mock_response(status_code=200, json_data=pdf_data)
            mock_post.return_value = response
            
            pdf = client.PDF(file=pdf_file)
            
            assert pdf.title == "Test PDF"
            assert pdf.is_rtl is False
            assert pdf.videos == []
            
            # Verify file was uploaded
            call_args = mock_post.call_args
            assert call_args[1]['files']['file'] == pdf_file


class TestErrorHandlingIntegration:
    """Integration tests for error handling across the library."""
    
    def test_error_propagation_through_client(self, api_key, base_url):
        """Test that errors are properly propagated through client methods."""
        client = InstaparserClient(api_key=api_key, base_url=base_url)
        
        error_codes = [
            (400, InstaparserValidationError),
            (401, InstaparserAuthenticationError),
            (403, InstaparserAPIError),
            (409, InstaparserAPIError),
            (429, InstaparserRateLimitError),
            (500, InstaparserAPIError),
        ]
        
        for status_code, expected_exception in error_codes:
            with patch.object(client.session, 'post') as mock_post:
                error_response = Mock(spec=requests.Response)
                error_response.status_code = status_code
                error_response.json.return_value = {"reason": f"Error {status_code}"}
                error_response.headers = {}
                mock_post.return_value = error_response
                
                with pytest.raises(expected_exception) as exc_info:
                    client.Article(url="https://example.com/article")
                
                assert exc_info.value.status_code == status_code


class TestMultipleClientInstances:
    """Tests for using multiple client instances."""
    
    def test_multiple_clients_independent(self):
        """Test that multiple client instances are independent."""
        client1 = InstaparserClient(api_key="key1", base_url="https://api1.com")
        client2 = InstaparserClient(api_key="key2", base_url="https://api2.com")
        
        assert client1.api_key == "key1"
        assert client2.api_key == "key2"
        assert client1.base_url == "https://api1.com"
        assert client2.base_url == "https://api2.com"
        assert client1.session is not client2.session
    
    def test_client_reuse_for_multiple_requests(self, api_key, base_url, mock_response):
        """Test reusing a client for multiple requests."""
        client = InstaparserClient(api_key=api_key, base_url=base_url)
        
        article_data = {
            "url": "https://example.com/article",
            "title": "Test Article",
            "html": "<p>Content</p>",
        }
        
        with patch.object(client.session, 'post') as mock_post:
            response = mock_response(status_code=200, json_data=article_data)
            mock_post.return_value = response
            
            # Make multiple requests
            article1 = client.Article(url="https://example.com/article1")
            article2 = client.Article(url="https://example.com/article2")
            
            assert mock_post.call_count == 2
            assert article1.title == "Test Article"
            assert article2.title == "Test Article"


class TestOutputFormats:
    """Tests for different output formats."""
    
    def test_article_html_vs_text_output(self, api_key, base_url, mock_response):
        """Test Article with HTML and text outputs."""
        client = InstaparserClient(api_key=api_key, base_url=base_url)
        
        html_data = {
            "url": "https://example.com/article",
            "html": "<p>HTML content</p>",
        }
        
        text_data = {
            "url": "https://example.com/article",
            "text": "Text content",
        }
        
        with patch.object(client.session, 'post') as mock_post:
            # Test HTML output
            response = mock_response(status_code=200, json_data=html_data)
            mock_post.return_value = response
            
            article_html = client.Article(
                url="https://example.com/article",
                output="html"
            )
            assert article_html.body == "<p>HTML content</p>"
            
            # Test text output
            response = mock_response(status_code=200, json_data=text_data)
            mock_post.return_value = response
            article_text = client.Article(
                url="https://example.com/article",
                output="text"
            )
            assert article_text.body == "Text content"
    
    def test_article_markdown_output(self, api_key, base_url, mock_response):
        """Test Article with markdown output."""
        client = InstaparserClient(api_key=api_key, base_url=base_url)
        
        markdown_data = {
            "url": "https://example.com/article",
            "markdown": "# Article Title\n\nMarkdown content",
        }
        
        with patch.object(client.session, 'post') as mock_post:
            response = mock_response(status_code=200, json_data=markdown_data)
            mock_post.return_value = response
            
            article = client.Article(
                url="https://example.com/article",
                output="markdown"
            )
            assert article.markdown == "# Article Title\n\nMarkdown content"
            assert article.body == "# Article Title\n\nMarkdown content"
    
    def test_pdf_html_vs_text_output(self, api_key, base_url, mock_response):
        """Test PDF with HTML and text outputs."""
        client = InstaparserClient(api_key=api_key, base_url=base_url)
        
        html_data = {
            "url": "https://example.com/document.pdf",
            "html": "<p>PDF HTML</p>",
        }
        
        text_data = {
            "url": "https://example.com/document.pdf",
            "text": "PDF Text",
        }
        
        with patch.object(client.session, 'get') as mock_get:
            # Test HTML output
            response = mock_response(status_code=200, json_data=html_data)
            mock_get.return_value = response
            
            pdf_html = client.PDF(
                url="https://example.com/document.pdf",
                output="html"
            )
            assert pdf_html.body == "<p>PDF HTML</p>"
            
            # Test text output
            response = mock_response(status_code=200, json_data=text_data)
            mock_get.return_value = response
            pdf_text = client.PDF(
                url="https://example.com/document.pdf",
                output="text"
            )
            assert pdf_text.body == "PDF Text"
    
    def test_pdf_markdown_output(self, api_key, base_url, mock_response):
        """Test PDF with markdown output."""
        client = InstaparserClient(api_key=api_key, base_url=base_url)
        
        markdown_data = {
            "url": "https://example.com/document.pdf",
            "markdown": "# PDF Title\n\nPDF markdown content",
        }
        
        with patch.object(client.session, 'get') as mock_get:
            response = mock_response(status_code=200, json_data=markdown_data)
            mock_get.return_value = response
            
            pdf = client.PDF(
                url="https://example.com/document.pdf",
                output="markdown"
            )
            assert pdf.markdown == "# PDF Title\n\nPDF markdown content"
            assert pdf.body == "# PDF Title\n\nPDF markdown content"
