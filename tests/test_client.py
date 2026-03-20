"""
Tests for InstaparserClient class.
"""

import json
from unittest.mock import Mock, MagicMock, patch, call
import pytest
import requests
from instaparser import InstaparserClient
from instaparser.exceptions import (
    InstaparserAPIError,
    InstaparserAuthenticationError,
    InstaparserRateLimitError,
    InstaparserValidationError,
)


class TestInstaparserClientInitialization:
    """Tests for InstaparserClient initialization."""
    
    def test_client_initialization_with_api_key(self, api_key):
        """Test client initialization with API key."""
        client = InstaparserClient(api_key=api_key)
        
        assert client.api_key == api_key
        assert client.base_url == InstaparserClient.BASE_URL
        assert client.session is not None
        assert client.session.headers['Authorization'] == f'Bearer {api_key}'
        assert client.session.headers['Content-Type'] == 'application/json'
    
    def test_client_initialization_with_custom_base_url(self, api_key, base_url):
        """Test client initialization with custom base URL."""
        client = InstaparserClient(api_key=api_key, base_url=base_url)
        
        assert client.api_key == api_key
        assert client.base_url == base_url
    
    def test_client_uses_default_base_url(self, api_key):
        """Test that client uses default base URL when not provided."""
        client = InstaparserClient(api_key=api_key)
        
        assert client.base_url == "https://instaparser.com"


class TestInstaparserClientHandleResponse:
    """Tests for _handle_response method."""
    
    def test_handle_response_success(self, client, mock_response):
        """Test handling successful response."""
        json_data = {"key": "value"}
        response = mock_response(status_code=200, json_data=json_data)
        
        result = client._handle_response(response)
        
        assert result == json_data
    
    def test_handle_response_non_json_success(self, client, mock_response):
        """Test handling successful non-JSON response."""
        response = mock_response(status_code=200, text="Plain text response")
        
        result = client._handle_response(response)
        
        assert result == {'raw': 'Plain text response'}
    
    def test_handle_response_401_authentication_error(self, client, mock_response):
        """Test handling 401 authentication error."""
        error_data = {"reason": "Invalid API key"}
        response = mock_response(status_code=401, json_data=error_data)
        
        with pytest.raises(InstaparserAuthenticationError) as exc_info:
            client._handle_response(response)
        
        assert exc_info.value.status_code == 401
        assert "Invalid API key" in str(exc_info.value)
        assert exc_info.value.response == response
    
    def test_handle_response_403_account_suspended(self, client, mock_response):
        """Test handling 403 account suspended error."""
        error_data = {"reason": "Account suspended"}
        response = mock_response(status_code=403, json_data=error_data)
        
        with pytest.raises(InstaparserAPIError) as exc_info:
            client._handle_response(response)
        
        assert exc_info.value.status_code == 403
        assert "Account suspended" in str(exc_info.value)
    
    def test_handle_response_409_monthly_limit(self, client, mock_response):
        """Test handling 409 monthly limit exceeded error."""
        error_data = {"reason": "Monthly API calls exceeded"}
        response = mock_response(status_code=409, json_data=error_data)
        
        with pytest.raises(InstaparserAPIError) as exc_info:
            client._handle_response(response)
        
        assert exc_info.value.status_code == 409
        assert "Monthly API calls exceeded" in str(exc_info.value)
    
    def test_handle_response_429_rate_limit_error(self, client, mock_response):
        """Test handling 429 rate limit error."""
        error_data = {"reason": "Rate limit exceeded"}
        response = mock_response(status_code=429, json_data=error_data)
        
        with pytest.raises(InstaparserRateLimitError) as exc_info:
            client._handle_response(response)
        
        assert exc_info.value.status_code == 429
        assert "Rate limit exceeded" in str(exc_info.value)
    
    def test_handle_response_400_validation_error(self, client, mock_response):
        """Test handling 400 validation error."""
        error_data = {"reason": "Invalid request parameters"}
        response = mock_response(status_code=400, json_data=error_data)
        
        with pytest.raises(InstaparserValidationError) as exc_info:
            client._handle_response(response)
        
        assert exc_info.value.status_code == 400
        assert "Invalid request parameters" in str(exc_info.value)
    
    def test_handle_response_500_generic_error(self, client, mock_response):
        """Test handling 500 generic API error."""
        error_data = {"reason": "Internal server error"}
        response = mock_response(status_code=500, json_data=error_data)
        
        with pytest.raises(InstaparserAPIError) as exc_info:
            client._handle_response(response)
        
        assert exc_info.value.status_code == 500
        assert "Internal server error" in str(exc_info.value)
    
    def test_handle_response_error_without_reason(self, client, mock_response):
        """Test handling error response without reason field."""
        response = mock_response(status_code=500, json_data={})
        
        with pytest.raises(InstaparserAPIError) as exc_info:
            client._handle_response(response)
        
        assert exc_info.value.status_code == 500
        assert "API request failed" in str(exc_info.value)
    
    def test_handle_response_error_with_text_only(self, client, mock_response):
        """Test handling error response with text only (no JSON)."""
        response = mock_response(status_code=500, text="Error message")
        
        with pytest.raises(InstaparserAPIError) as exc_info:
            client._handle_response(response)
        
        assert exc_info.value.status_code == 500
        assert "Error message" in str(exc_info.value)


class TestInstaparserClientArticle:
    """Tests for Article method."""
    
    def test_article_from_url(self, client, mock_article_response, mock_response):
        """Test parsing article from URL."""
        with patch.object(client.session, 'post') as mock_post:
            response = mock_response(status_code=200, json_data=mock_article_response)
            mock_post.return_value = response
            
            article = client.Article(url="https://example.com/article")
            
            assert article.title == "Test Article Title"
            assert article.url == "https://example.com/article"
            assert article.body == "<p>This is the article body in HTML format.</p>"
            
            # Verify API call
            mock_post.assert_called_once()
            call_args = mock_post.call_args
            assert '/api/1/article' in call_args[0][0]
            assert call_args[1]['json']['url'] == "https://example.com/article"
            assert call_args[1]['json']['output'] == 'html'
            assert 'use_cache' not in call_args[1]['json']  # Default is True, not sent
    
    def test_article_with_text_output(self, client, mock_article_text_response, mock_response):
        """Test parsing article with text output."""
        with patch.object(client.session, 'post') as mock_post:
            response = mock_response(status_code=200, json_data=mock_article_text_response)
            mock_post.return_value = response
            
            article = client.Article(
                url="https://example.com/article",
                output="text"
            )
            
            assert article.text == "This is the article body in plain text format."
            assert article.body == "This is the article body in plain text format."
            
            call_args = mock_post.call_args
            assert call_args[1]['json']['output'] == 'text'
    
    def test_article_with_content(self, client, mock_article_response, mock_response):
        """Test parsing article with HTML content."""
        html_content = "<html><body>Test content</body></html>"
        
        with patch.object(client.session, 'post') as mock_post:
            response = mock_response(status_code=200, json_data=mock_article_response)
            mock_post.return_value = response
            
            article = client.Article(
                url="https://example.com/article",
                content=html_content
            )
            
            call_args = mock_post.call_args
            assert call_args[1]['json']['content'] == html_content
    
    def test_article_with_use_cache_false(self, client, mock_article_response, mock_response):
        """Test parsing article with use_cache=False."""
        with patch.object(client.session, 'post') as mock_post:
            response = mock_response(status_code=200, json_data=mock_article_response)
            mock_post.return_value = response
            
            client.Article(
                url="https://example.com/article",
                use_cache=False
            )
            
            call_args = mock_post.call_args
            assert call_args[1]['json']['use_cache'] == 'false'
    
    def test_article_with_markdown_output(self, client, mock_response):
        """Test parsing article with markdown output."""
        markdown_response = {
            "url": "https://example.com/article",
            "title": "Test Article",
            "markdown": "# Test Article\n\nMarkdown body content.",
        }
        with patch.object(client.session, 'post') as mock_post:
            response = mock_response(status_code=200, json_data=markdown_response)
            mock_post.return_value = response
            
            article = client.Article(
                url="https://example.com/article",
                output="markdown"
            )
            
            assert article.markdown == "# Test Article\n\nMarkdown body content."
            assert article.body == "# Test Article\n\nMarkdown body content."
            
            call_args = mock_post.call_args
            assert call_args[1]['json']['output'] == 'markdown'
    
    def test_article_invalid_output(self, client):
        """Test that invalid output format raises ValidationError."""
        with pytest.raises(InstaparserValidationError) as exc_info:
            client.Article(url="https://example.com/article", output="invalid")
        
        assert "output must be 'html', 'text', or 'markdown'" in str(exc_info.value)


class TestInstaparserClientSummary:
    """Tests for Summary method."""
    
    def test_summary_from_url(self, client, mock_summary_response, mock_response):
        """Test generating summary from URL."""
        with patch.object(client.session, 'post') as mock_post:
            response = mock_response(status_code=200, json_data=mock_summary_response)
            mock_post.return_value = response
            
            summary = client.Summary(url="https://example.com/article")
            
            assert len(summary.key_sentences) == 3
            assert summary.overview == "This is a comprehensive overview of the article content."
            
            call_args = mock_post.call_args
            assert '/api/1/summary' in call_args[0][0]
            assert call_args[1]['json']['url'] == "https://example.com/article"
            assert call_args[1]['json']['stream'] is False
    
    def test_summary_with_content(self, client, mock_summary_response, mock_response):
        """Test generating summary with HTML content."""
        html_content = "<html><body>Test content</body></html>"
        
        with patch.object(client.session, 'post') as mock_post:
            response = mock_response(status_code=200, json_data=mock_summary_response)
            mock_post.return_value = response
            
            summary = client.Summary(
                url="https://example.com/article",
                content=html_content
            )
            
            call_args = mock_post.call_args
            assert call_args[1]['json']['content'] == html_content
    
    def test_summary_with_use_cache_false(self, client, mock_summary_response, mock_response):
        """Test generating summary with use_cache=False."""
        with patch.object(client.session, 'post') as mock_post:
            response = mock_response(status_code=200, json_data=mock_summary_response)
            mock_post.return_value = response
            
            client.Summary(
                url="https://example.com/article",
                use_cache=False
            )
            
            call_args = mock_post.call_args
            assert call_args[1]['json']['use_cache'] == 'false'
    
    def test_summary_with_streaming_callback(self, client):
        """Test generating summary with streaming callback."""
        # Mock streaming response
        stream_lines = [
            b'key_sentences: ["Sentence 1", "Sentence 2"]',
            b'delta: This is',
            b'delta:  a streaming',
            b'delta:  overview.',
        ]
        
        with patch.object(client.session, 'post') as mock_post:
            streaming_response = Mock(spec=requests.Response)
            streaming_response.status_code = 200
            streaming_response.iter_lines.return_value = stream_lines
            streaming_response.headers = {}
            mock_post.return_value = streaming_response
            
            received_lines = []
            def stream_callback(line):
                received_lines.append(line)
            
            summary = client.Summary(
                url="https://example.com/article",
                stream_callback=stream_callback
            )
            
            # Verify callback was called for each line
            assert len(received_lines) == 4
            assert received_lines[0] == 'key_sentences: ["Sentence 1", "Sentence 2"]'
            
            # Verify summary was constructed from stream
            assert len(summary.key_sentences) == 2
            assert summary.overview == "This is a streaming overview."
            
            # Verify stream=True was set
            call_args = mock_post.call_args
            assert call_args[1]['json']['stream'] is True
            assert call_args[1]['stream'] is True
    
    def test_summary_streaming_with_error(self, client, mock_response):
        """Test that streaming errors are handled."""
        with patch.object(client.session, 'post') as mock_post:
            error_response = mock_response(status_code=401, json_data={"reason": "Invalid API key"})
            mock_post.return_value = error_response
            
            with pytest.raises(InstaparserAuthenticationError):
                client.Summary(
                    url="https://example.com/article",
                    stream_callback=lambda x: None
                )


class TestInstaparserClientPDF:
    """Tests for PDF method."""
    
    def test_pdf_from_url_get(self, client, mock_pdf_response, mock_response):
        """Test parsing PDF from URL using GET request."""
        with patch.object(client.session, 'get') as mock_get:
            response = mock_response(status_code=200, json_data=mock_pdf_response)
            mock_get.return_value = response
            
            pdf = client.PDF(url="https://example.com/document.pdf")
            
            assert pdf.title == "Test PDF Document"
            assert pdf.url == "https://example.com/document.pdf"
            assert pdf.is_rtl is False
            assert pdf.videos == []
            
            call_args = mock_get.call_args
            assert '/api/1/pdf' in call_args[0][0]
            assert call_args[1]['params']['url'] == "https://example.com/document.pdf"
            assert call_args[1]['params']['output'] == 'html'
    
    def test_pdf_from_file_post(self, client, mock_pdf_response, mock_response):
        """Test parsing PDF from file using POST request."""
        pdf_file = Mock()
        pdf_file.read.return_value = b"PDF content"
        
        with patch.object(client.session, 'post') as mock_post:
            response = mock_response(status_code=200, json_data=mock_pdf_response)
            mock_post.return_value = response
            
            pdf = client.PDF(file=pdf_file)
            
            assert pdf.title == "Test PDF Document"
            
            call_args = mock_post.call_args
            assert '/api/1/pdf' in call_args[0][0]
            assert 'files' in call_args[1]
            assert call_args[1]['files']['file'] == pdf_file
            # Content-Type should be removed for multipart/form-data
            assert 'Content-Type' not in call_args[1].get('headers', {})
    
    def test_pdf_from_file_bytes(self, client, mock_pdf_response, mock_response):
        """Test parsing PDF from bytes."""
        pdf_bytes = b"PDF content bytes"
        
        with patch.object(client.session, 'post') as mock_post:
            response = mock_response(status_code=200, json_data=mock_pdf_response)
            mock_post.return_value = response
            
            pdf = client.PDF(file=pdf_bytes)
            
            assert pdf.title == "Test PDF Document"
            call_args = mock_post.call_args
            assert call_args[1]['files']['file'] == pdf_bytes
    
    def test_pdf_with_text_output(self, client, mock_pdf_response, mock_response):
        """Test parsing PDF with text output."""
        with patch.object(client.session, 'get') as mock_get:
            pdf_response = dict(mock_pdf_response)
            pdf_response['text'] = "PDF content in text"
            pdf_response.pop('html', None)
            response = mock_response(status_code=200, json_data=pdf_response)
            mock_get.return_value = response
            
            pdf = client.PDF(
                url="https://example.com/document.pdf",
                output="text"
            )
            
            call_args = mock_get.call_args
            assert call_args[1]['params']['output'] == 'text'
    
    def test_pdf_with_use_cache_false(self, client, mock_pdf_response, mock_response):
        """Test parsing PDF with use_cache=False."""
        with patch.object(client.session, 'get') as mock_get:
            response = mock_response(status_code=200, json_data=mock_pdf_response)
            mock_get.return_value = response
            
            client.PDF(
                url="https://example.com/document.pdf",
                use_cache=False
            )
            
            call_args = mock_get.call_args
            assert call_args[1]['params']['use_cache'] == 'false'
    
    def test_pdf_with_file_and_url(self, client, mock_pdf_response, mock_response):
        """Test parsing PDF with both file and URL (should use POST)."""
        pdf_file = Mock()
        
        with patch.object(client.session, 'post') as mock_post:
            response = mock_response(status_code=200, json_data=mock_pdf_response)
            mock_post.return_value = response
            
            client.PDF(
                url="https://example.com/document.pdf",
                file=pdf_file
            )
            
            call_args = mock_post.call_args
            assert call_args[1]['data']['url'] == "https://example.com/document.pdf"
    
    def test_pdf_with_markdown_output(self, client, mock_pdf_response, mock_response):
        """Test parsing PDF with markdown output."""
        with patch.object(client.session, 'get') as mock_get:
            pdf_response = dict(mock_pdf_response)
            pdf_response['markdown'] = "# PDF Document\n\nPDF content in markdown"
            pdf_response.pop('html', None)
            response = mock_response(status_code=200, json_data=pdf_response)
            mock_get.return_value = response
            
            pdf = client.PDF(
                url="https://example.com/document.pdf",
                output="markdown"
            )
            
            call_args = mock_get.call_args
            assert call_args[1]['params']['output'] == 'markdown'
    
    def test_pdf_invalid_output(self, client):
        """Test that invalid output format raises ValidationError."""
        with pytest.raises(InstaparserValidationError) as exc_info:
            client.PDF(url="https://example.com/document.pdf", output="invalid")
        
        assert "output must be 'html', 'text', or 'markdown'" in str(exc_info.value)
    
    def test_pdf_no_url_or_file(self, client):
        """Test that missing both url and file raises ValidationError."""
        with pytest.raises(InstaparserValidationError) as exc_info:
            client.PDF()
        
        assert "Either 'url' or 'file' must be provided" in str(exc_info.value)


class TestInstaparserClientEdgeCases:
    """Tests for edge cases and error scenarios."""
    
    def test_article_network_error(self, client):
        """Test handling network errors during Article request."""
        with patch.object(client.session, 'post') as mock_post:
            mock_post.side_effect = requests.exceptions.ConnectionError("Connection failed")
            
            with pytest.raises(requests.exceptions.ConnectionError):
                client.Article(url="https://example.com/article")
    
    def test_article_timeout_error(self, client):
        """Test handling timeout errors during Article request."""
        with patch.object(client.session, 'post') as mock_post:
            mock_post.side_effect = requests.exceptions.Timeout("Request timed out")
            
            with pytest.raises(requests.exceptions.Timeout):
                client.Article(url="https://example.com/article")
    
    def test_article_malformed_json_response(self, client, mock_response):
        """Test handling malformed JSON in successful response."""
        with patch.object(client.session, 'post') as mock_post:
            response = mock_response(status_code=200, text="Not valid JSON {")
            mock_post.return_value = response
            
            # When JSON parsing fails, _handle_response returns {'raw': text}
            # This will cause Article initialization to fail or have None values
            # The test verifies the client handles this gracefully
            from instaparser.article import Article
            result = client.Article(url="https://example.com/article")
            # Article should still be created, but may have None/empty values
            assert isinstance(result, Article)
    
    def test_summary_empty_response(self, client, mock_response):
        """Test handling empty summary response."""
        with patch.object(client.session, 'post') as mock_post:
            response = mock_response(status_code=200, json_data={})
            mock_post.return_value = response
            
            summary = client.Summary(url="https://example.com/article")
            assert summary.key_sentences == []
            assert summary.overview == ""
    
    def test_summary_streaming_empty_lines(self, client):
        """Test handling empty lines in streaming response."""
        stream_lines = [
            b'key_sentences: []',
            b'',
            b'delta: Content',
            b'',
        ]
        
        with patch.object(client.session, 'post') as mock_post:
            streaming_response = Mock(spec=requests.Response)
            streaming_response.status_code = 200
            streaming_response.iter_lines.return_value = stream_lines
            streaming_response.headers = {}
            mock_post.return_value = streaming_response
            
            received_lines = []
            def stream_callback(line):
                received_lines.append(line)
            
            summary = client.Summary(
                url="https://example.com/article",
                stream_callback=stream_callback
            )
            
            # Empty lines should be filtered out by iter_lines check
            assert summary.overview == "Content"
    
    def test_summary_streaming_malformed_key_sentences(self, client):
        """Test handling malformed key_sentences in streaming response raises InstaparserAPIError."""
        stream_lines = [
            b'key_sentences: not valid json',
            b'delta: Content',
        ]
        
        with patch.object(client.session, 'post') as mock_post:
            streaming_response = Mock(spec=requests.Response)
            streaming_response.status_code = 200
            streaming_response.iter_lines.return_value = stream_lines
            streaming_response.headers = {}
            mock_post.return_value = streaming_response
            
            def stream_callback(line):
                pass
            
            # Should raise InstaparserAPIError when key_sentences JSON is malformed
            with pytest.raises(InstaparserAPIError) as exc_info:
                client.Summary(
                    url="https://example.com/article",
                    stream_callback=stream_callback
                )
            
            # Verify the exception has the correct message and status_code (from line 222)
            assert exc_info.value.status_code == 412
            assert 'Unable to generate key sentences' in str(exc_info.value)
    
    def test_pdf_file_with_url_parameter(self, client, mock_pdf_response, mock_response):
        """Test PDF with both file and URL parameters."""
        pdf_file = Mock()
        
        with patch.object(client.session, 'post') as mock_post:
            response = mock_response(status_code=200, json_data=mock_pdf_response)
            mock_post.return_value = response
            
            pdf = client.PDF(
                url="https://example.com/document.pdf",
                file=pdf_file
            )
            
            call_args = mock_post.call_args
            assert call_args[1]['data']['url'] == "https://example.com/document.pdf"
            assert call_args[1]['files']['file'] == pdf_file
    
    def test_pdf_file_like_object(self, client, mock_pdf_response, mock_response):
        """Test PDF with file-like object."""
        class FileLike:
            def read(self):
                return b"PDF content"
        
        file_like = FileLike()
        
        with patch.object(client.session, 'post') as mock_post:
            response = mock_response(status_code=200, json_data=mock_pdf_response)
            mock_post.return_value = response
            
            pdf = client.PDF(file=file_like)
            
            call_args = mock_post.call_args
            assert call_args[1]['files']['file'] == file_like
    
    def test_article_url_encoding(self, client, mock_article_response, mock_response):
        """Test Article with URL containing special characters."""
        special_url = "https://example.com/article?param=value&other=test"
        
        with patch.object(client.session, 'post') as mock_post:
            response = mock_response(status_code=200, json_data=mock_article_response)
            mock_post.return_value = response
            
            article = client.Article(url=special_url)
            
            call_args = mock_post.call_args
            assert call_args[1]['json']['url'] == special_url
    
    def test_summary_url_encoding(self, client, mock_summary_response, mock_response):
        """Test Summary with URL containing special characters."""
        special_url = "https://example.com/article?param=value&other=test"
        
        with patch.object(client.session, 'post') as mock_post:
            response = mock_response(status_code=200, json_data=mock_summary_response)
            mock_post.return_value = response
            
            summary = client.Summary(url=special_url)
            
            call_args = mock_post.call_args
            assert call_args[1]['json']['url'] == special_url
    
    def test_pdf_url_encoding(self, client, mock_pdf_response, mock_response):
        """Test PDF with URL containing special characters."""
        special_url = "https://example.com/document.pdf?param=value"
        
        with patch.object(client.session, 'get') as mock_get:
            response = mock_response(status_code=200, json_data=mock_pdf_response)
            mock_get.return_value = response
            
            pdf = client.PDF(url=special_url)
            
            call_args = mock_get.call_args
            assert call_args[1]['params']['url'] == special_url
    
    def test_article_large_content(self, client, mock_article_response, mock_response):
        """Test Article with large HTML content."""
        large_content = "<html>" + "<p>Content</p>" * 10000 + "</html>"
        
        with patch.object(client.session, 'post') as mock_post:
            response = mock_response(status_code=200, json_data=mock_article_response)
            mock_post.return_value = response
            
            article = client.Article(
                url="https://example.com/article",
                content=large_content
            )
            
            call_args = mock_post.call_args
            assert call_args[1]['json']['content'] == large_content
    
    def test_summary_large_content(self, client, mock_summary_response, mock_response):
        """Test Summary with large HTML content."""
        large_content = "<html>" + "<p>Content</p>" * 10000 + "</html>"
        
        with patch.object(client.session, 'post') as mock_post:
            response = mock_response(status_code=200, json_data=mock_summary_response)
            mock_post.return_value = response
            
            summary = client.Summary(
                url="https://example.com/article",
                content=large_content
            )
            
            call_args = mock_post.call_args
            assert call_args[1]['json']['content'] == large_content
    
    def test_pdf_large_file(self, client, mock_pdf_response, mock_response):
        """Test PDF with large file."""
        large_file = b"PDF content " * 100000
        
        with patch.object(client.session, 'post') as mock_post:
            response = mock_response(status_code=200, json_data=mock_pdf_response)
            mock_post.return_value = response
            
            pdf = client.PDF(file=large_file)
            
            call_args = mock_post.call_args
            assert call_args[1]['files']['file'] == large_file
    
    def test_handle_response_empty_error_text(self, client, mock_response):
        """Test handling error response with empty text."""
        response = mock_response(status_code=500, text="")
        
        with pytest.raises(InstaparserAPIError) as exc_info:
            client._handle_response(response)
        
        assert exc_info.value.status_code == 500
    
    def test_handle_response_error_with_none_text(self, client):
        """Test handling error response with None text."""
        response = Mock(spec=requests.Response)
        response.status_code = 500
        response.text = None
        response.json.side_effect = ValueError("Not JSON")
        response.headers = {}
        
        with pytest.raises(InstaparserAPIError) as exc_info:
            client._handle_response(response)
        
        assert exc_info.value.status_code == 500
    
    def test_session_headers_preserved(self, api_key):
        """Test that session headers are properly set and preserved."""
        client = InstaparserClient(api_key=api_key)
        
        # Headers should be set
        assert 'Authorization' in client.session.headers
        assert 'Content-Type' in client.session.headers
        
        # Headers should persist
        assert client.session.headers['Authorization'] == f'Bearer {api_key}'
        assert client.session.headers['Content-Type'] == 'application/json'
    
    def test_base_url_joining(self, api_key, mock_response):
        """Test that base URL is properly joined with endpoints."""
        custom_base = "https://api.test.com"
        client = InstaparserClient(api_key=api_key, base_url=custom_base)
        
        with patch.object(client.session, 'post') as mock_post:
            response = mock_response(status_code=200, json_data={})
            mock_post.return_value = response
            
            client.Article(url="https://example.com/article")
            
            call_args = mock_post.call_args
            assert call_args[0][0].startswith(custom_base)
            assert '/api/1/article' in call_args[0][0]
    
    def test_base_url_with_trailing_slash(self, api_key, mock_response):
        """Test base URL with trailing slash is handled correctly."""
        custom_base = "https://api.test.com/"
        client = InstaparserClient(api_key=api_key, base_url=custom_base)
        
        with patch.object(client.session, 'post') as mock_post:
            response = mock_response(status_code=200, json_data={})
            mock_post.return_value = response
            
            client.Article(url="https://example.com/article")
            
            call_args = mock_post.call_args
            # urljoin should handle trailing slash correctly
            assert '/api/1/article' in call_args[0][0]
    
    def test_article_content_with_use_cache_false(self, client, mock_article_response, mock_response):
        """Test Article with both content and use_cache=False."""
        html_content = "<html><body>Test</body></html>"
        
        with patch.object(client.session, 'post') as mock_post:
            response = mock_response(status_code=200, json_data=mock_article_response)
            mock_post.return_value = response
            
            client.Article(
                url="https://example.com/article",
                content=html_content,
                use_cache=False
            )
            
            call_args = mock_post.call_args
            assert call_args[1]['json']['content'] == html_content
            assert call_args[1]['json']['use_cache'] == 'false'
    
    def test_summary_content_with_use_cache_false(self, client, mock_summary_response, mock_response):
        """Test Summary with both content and use_cache=False."""
        html_content = "<html><body>Test</body></html>"
        
        with patch.object(client.session, 'post') as mock_post:
            response = mock_response(status_code=200, json_data=mock_summary_response)
            mock_post.return_value = response
            
            client.Summary(
                url="https://example.com/article",
                content=html_content,
                use_cache=False
            )
            
            call_args = mock_post.call_args
            assert call_args[1]['json']['content'] == html_content
            assert call_args[1]['json']['use_cache'] == 'false'
    
    def test_pdf_file_with_use_cache_false(self, client, mock_pdf_response, mock_response):
        """Test PDF with file and use_cache=False."""
        pdf_file = Mock()
        
        with patch.object(client.session, 'post') as mock_post:
            response = mock_response(status_code=200, json_data=mock_pdf_response)
            mock_post.return_value = response
            
            client.PDF(
                file=pdf_file,
                use_cache=False
            )
            
            call_args = mock_post.call_args
            assert call_args[1]['data']['use_cache'] == 'false'
    
    def test_pdf_url_with_use_cache_false(self, client, mock_pdf_response, mock_response):
        """Test PDF with URL and use_cache=False."""
        with patch.object(client.session, 'get') as mock_get:
            response = mock_response(status_code=200, json_data=mock_pdf_response)
            mock_get.return_value = response
            
            client.PDF(
                url="https://example.com/document.pdf",
                use_cache=False
            )
            
            call_args = mock_get.call_args
            assert call_args[1]['params']['use_cache'] == 'false'
    
    def test_summary_streaming_callback_called_for_each_line(self, client):
        """Test that streaming callback is called for each non-empty line."""
        stream_lines = [
            b'key_sentences: ["S1"]',
            b'delta: Line 1',
            b'delta: Line 2',
            b'delta: Line 3',
        ]
        
        with patch.object(client.session, 'post') as mock_post:
            streaming_response = Mock(spec=requests.Response)
            streaming_response.status_code = 200
            streaming_response.iter_lines.return_value = stream_lines
            streaming_response.headers = {}
            mock_post.return_value = streaming_response
            
            callback_calls = []
            def stream_callback(line):
                callback_calls.append(line)
            
            client.Summary(
                url="https://example.com/article",
                stream_callback=stream_callback
            )
            
            assert len(callback_calls) == 4
            assert callback_calls[0] == 'key_sentences: ["S1"]'
            assert callback_calls[1] == 'delta: Line 1'
            assert callback_calls[2] == 'delta: Line 2'
            assert callback_calls[3] == 'delta: Line 3'
    
    def test_pdf_multipart_form_data_headers(self, client, mock_pdf_response, mock_response):
        """Test that Content-Type header is removed for multipart form data."""
        pdf_file = Mock()
        
        with patch.object(client.session, 'post') as mock_post:
            response = mock_response(status_code=200, json_data=mock_pdf_response)
            mock_post.return_value = response
            
            client.PDF(file=pdf_file)
            
            call_args = mock_post.call_args
            headers = call_args[1].get('headers', {})
            # Content-Type should not be in headers (requests will set it for multipart)
            assert 'Content-Type' not in headers or headers.get('Content-Type') != 'application/json'
