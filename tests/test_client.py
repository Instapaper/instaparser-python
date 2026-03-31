import io
import json
from unittest.mock import Mock
from urllib.error import HTTPError, URLError

import pytest

from instaparser import InstaparserClient
from instaparser.article import Article
from instaparser.client import _encode_multipart_formdata
from instaparser.exceptions import (
    InstaparserAPIError,
    InstaparserAuthenticationError,
    InstaparserRateLimitError,
    InstaparserValidationError,
)

API_KEY = "test-api-key-12345"
BASE_URL = "https://api.test.instaparser.com"

ARTICLE_DATA = {
    "url": "https://example.com/article",
    "title": "Test Article Title",
    "site_name": "Example Site",
    "author": "John Doe",
    "date": 1609459200,
    "description": "This is a test article description",
    "thumbnail": "https://example.com/thumb.jpg",
    "words": 500,
    "is_rtl": False,
    "images": ["https://example.com/image1.jpg"],
    "videos": [],
    "html": "<p>This is the article body in HTML format.</p>",
}

SUMMARY_DATA = {
    "key_sentences": [
        "This is the first key sentence.",
        "This is the second key sentence.",
        "This is the third key sentence.",
    ],
    "overview": "This is a comprehensive overview of the article content.",
}

PDF_DATA = {
    "url": "https://example.com/document.pdf",
    "title": "Test PDF Document",
    "site_name": "Example Site",
    "author": "Jane Smith",
    "date": 1609459200,
    "description": "This is a test PDF document",
    "thumbnail": None,
    "words": 1000,
    "is_rtl": False,
    "images": [],
    "videos": [],
    "html": "<p>This is the PDF content in HTML format.</p>",
}

ERROR_CODES = [
    (400, InstaparserValidationError),
    (401, InstaparserAuthenticationError),
    (403, InstaparserAPIError),
    (409, InstaparserAPIError),
    (429, InstaparserRateLimitError),
    (500, InstaparserAPIError),
]


@pytest.fixture
def client():
    return InstaparserClient(api_key=API_KEY, base_url=BASE_URL)


@pytest.fixture
def mock_request(client, monkeypatch):
    mock = Mock()
    monkeypatch.setattr(client, "_request", mock)
    return mock


def make_response(*, json_data=None, text=None):
    """Mock a successful HTTPResponse."""
    response = Mock()
    response.status = 200
    if json_data is not None:
        response.read.return_value = json.dumps(json_data).encode()
    elif text is not None:
        response.read.return_value = text.encode()
    else:
        response.read.return_value = b"{}"
    return response


def make_streaming_response(lines):
    """Mock a streaming HTTPResponse that yields *lines*."""
    response = Mock()
    response.status = 200
    response.__iter__ = Mock(return_value=iter(lines))
    return response


def make_error(status_code, *, json_data=None, text=None):
    """Create an HTTPError with a readable body."""
    if json_data is not None:
        body = json.dumps(json_data).encode()
    elif text is not None:
        body = text.encode()
    else:
        body = b"{}"
    return HTTPError("https://api.example.com", status_code, "", None, io.BytesIO(body))


class TestClientInit:
    def test_base_url(self):
        client = InstaparserClient(api_key=API_KEY, base_url=BASE_URL)
        assert client.base_url == BASE_URL

    def test_headers(self):
        client = InstaparserClient(api_key=API_KEY)
        assert client.headers["Authorization"] == f"Bearer {API_KEY}"


class TestReadJson:
    def test_valid_json(self, client):
        assert client._read_json(make_response(json_data={"key": "value"})) == {"key": "value"}

    def test_non_json(self, client):
        assert client._read_json(make_response(text="Plain text")) == {"raw": "Plain text"}


class TestArticle:
    def test_basic_parse(self, client, mock_request):
        mock_request.return_value = make_response(json_data=ARTICLE_DATA)

        article = client.Article(url="https://example.com/article")

        assert article.title == "Test Article Title"
        assert article.url == "https://example.com/article"
        assert article.body == "<p>This is the article body in HTML format.</p>"

        _method, _path = mock_request.call_args[0]
        payload = mock_request.call_args[1]["json_data"]
        assert _method == "POST"
        assert _path == "/api/1/article"
        assert payload["url"] == "https://example.com/article"
        assert payload["output"] == "html"
        assert "use_cache" not in payload

    def test_text_output(self, client, mock_request):
        data = {**ARTICLE_DATA, "html": None, "text": "Plain text body."}
        mock_request.return_value = make_response(json_data=data)
        article = client.Article(url="u", output="text")

        assert article.body == "Plain text body."
        assert mock_request.call_args[1]["json_data"]["output"] == "text"

    def test_markdown_output(self, client, mock_request):
        mock_request.return_value = make_response(json_data={"url": "u", "markdown": "# MD"})
        article = client.Article(url="u", output="markdown")

        assert article.markdown == "# MD"
        assert article.body == "# MD"

    def test_with_content(self, client, mock_request):
        mock_request.return_value = make_response(json_data=ARTICLE_DATA)
        client.Article(url="u", content="<html>hi</html>")
        assert mock_request.call_args[1]["json_data"]["content"] == "<html>hi</html>"

    def test_use_cache_false(self, client, mock_request):
        mock_request.return_value = make_response(json_data=ARTICLE_DATA)
        client.Article(url="u", use_cache=False)
        assert mock_request.call_args[1]["json_data"]["use_cache"] == "false"

    def test_invalid_output(self, client):
        with pytest.raises(InstaparserValidationError, match="output must be"):
            client.Article(url="u", output="invalid")

    def test_malformed_json_response(self, client, mock_request):
        mock_request.return_value = make_response(text="Not valid JSON {")
        article = client.Article(url="u")
        assert isinstance(article, Article)


class TestSummary:
    def test_basic_summary(self, client, mock_request):
        mock_request.return_value = make_response(json_data=SUMMARY_DATA)

        summary = client.Summary(url="https://example.com/article")

        assert len(summary.key_sentences) == 3
        assert summary.overview == "This is a comprehensive overview of the article content."
        assert mock_request.call_args[1]["json_data"]["stream"] is False

    def test_with_content(self, client, mock_request):
        mock_request.return_value = make_response(json_data=SUMMARY_DATA)
        client.Summary(url="u", content="<html>hi</html>")
        assert mock_request.call_args[1]["json_data"]["content"] == "<html>hi</html>"

    def test_use_cache_false(self, client, mock_request):
        mock_request.return_value = make_response(json_data=SUMMARY_DATA)
        client.Summary(url="u", use_cache=False)
        assert mock_request.call_args[1]["json_data"]["use_cache"] == "false"

    def test_empty_response(self, client, mock_request):
        mock_request.return_value = make_response(json_data={})
        summary = client.Summary(url="u")
        assert summary.key_sentences == []
        assert summary.overview == ""

    def test_streaming_callback(self, client, mock_request):
        mock_request.return_value = make_streaming_response(
            [
                b'key_sentences: ["Sentence 1", "Sentence 2"]\r\n',
                b"delta: This is\r\n",
                b"delta:  a streaming\r\n",
                b"delta:  overview.\r\n",
            ]
        )

        received = []
        summary = client.Summary(url="u", stream_callback=received.append)

        assert len(received) == 4
        assert received[0] == 'key_sentences: ["Sentence 1", "Sentence 2"]'
        assert summary.key_sentences == ["Sentence 1", "Sentence 2"]
        assert summary.overview == "This is a streaming overview."
        assert mock_request.call_args[1]["json_data"]["stream"] is True

    def test_streaming_empty_lines_filtered(self, client, mock_request):
        mock_request.return_value = make_streaming_response(
            [
                b"key_sentences: []\r\n",
                b"\r\n",
                b"delta: Content\r\n",
                b"\r\n",
            ]
        )
        summary = client.Summary(url="u", stream_callback=lambda _: None)
        assert summary.overview == "Content"

    def test_streaming_malformed_key_sentences(self, client, mock_request):
        mock_request.return_value = make_streaming_response(
            [
                b"key_sentences: not valid json\r\n",
                b"delta: Content\r\n",
            ]
        )
        with pytest.raises(InstaparserAPIError) as exc_info:
            client.Summary(url="u", stream_callback=lambda _: None)
        assert exc_info.value.status_code == 412
        assert "Unable to generate key sentences" in str(exc_info.value)

    def test_streaming_error_response(self, client, mock_request):
        mock_request.side_effect = make_error(401, json_data={"reason": "Invalid API key"})
        with pytest.raises(InstaparserAuthenticationError):
            client.Summary(url="u", stream_callback=lambda _: None)


class TestPDF:
    def test_from_url(self, client, mock_request):
        mock_request.return_value = make_response(json_data=PDF_DATA)

        pdf = client.PDF(url="https://example.com/document.pdf")

        assert pdf.title == "Test PDF Document"
        assert pdf.is_rtl is False
        assert pdf.videos == []
        _method, _path = mock_request.call_args[0]
        assert _method == "GET"
        assert _path == "/api/1/pdf"
        assert mock_request.call_args[1]["params"]["url"] == "https://example.com/document.pdf"

    def test_from_file(self, client, mock_request):
        pdf_file = Mock()
        mock_request.return_value = make_response(json_data=PDF_DATA)

        pdf = client.PDF(file=pdf_file)

        assert pdf.title == "Test PDF Document"
        assert mock_request.call_args[0][0] == "POST"
        assert mock_request.call_args[1]["multipart_files"]["file"] is pdf_file

    def test_from_bytes(self, client, mock_request):
        mock_request.return_value = make_response(json_data=PDF_DATA)
        client.PDF(file=b"PDF content")
        assert mock_request.call_args[1]["multipart_files"]["file"] == b"PDF content"

    def test_file_and_url(self, client, mock_request):
        """When both file and url are given, POST with url in form fields."""
        pdf_file = Mock()
        mock_request.return_value = make_response(json_data=PDF_DATA)
        client.PDF(url="https://example.com/document.pdf", file=pdf_file)
        assert mock_request.call_args[1]["multipart_fields"]["url"] == "https://example.com/document.pdf"

    @pytest.mark.parametrize("output", ["text", "markdown"])
    def test_output_formats_url(self, client, mock_request, output):
        data = {**PDF_DATA, "html": None, output: f"content in {output}"}
        mock_request.return_value = make_response(json_data=data)
        client.PDF(url="https://example.com/document.pdf", output=output)
        assert mock_request.call_args[1]["params"]["output"] == output

    def test_use_cache_false_url(self, client, mock_request):
        mock_request.return_value = make_response(json_data=PDF_DATA)
        client.PDF(url="https://example.com/document.pdf", use_cache=False)
        assert mock_request.call_args[1]["params"]["use_cache"] == "false"

    def test_use_cache_false_file(self, client, mock_request):
        mock_request.return_value = make_response(json_data=PDF_DATA)
        client.PDF(file=Mock(), use_cache=False)
        assert mock_request.call_args[1]["multipart_fields"]["use_cache"] == "false"

    def test_invalid_output(self, client):
        with pytest.raises(InstaparserValidationError, match="output must be"):
            client.PDF(url="u", output="invalid")

    def test_no_url_or_file(self, client):
        with pytest.raises(InstaparserValidationError, match="Either 'url' or 'file'"):
            client.PDF()


class TestTransportErrors:
    def test_url_error(self, client, mock_request):
        mock_request.side_effect = URLError("Connection failed")
        with pytest.raises(URLError):
            client.Article(url="u")

    def test_timeout_error(self, client, mock_request):
        mock_request.side_effect = TimeoutError("timed out")
        with pytest.raises(TimeoutError):
            client.Article(url="u")


class TestURLConstruction:
    @pytest.mark.parametrize("base", ["https://api.test.com", "https://api.test.com/"])
    def test_base_url_joining(self, base, monkeypatch):
        client = InstaparserClient(api_key=API_KEY, base_url=base)
        mock_urlopen = Mock(return_value=make_response(json_data={}))
        monkeypatch.setattr("instaparser.client.urlopen", mock_urlopen)
        client.Article(url="u")
        req = mock_urlopen.call_args[0][0]
        assert req.full_url.startswith("https://api.test.com/api/1/article")


class TestMultipleClients:
    def test_independent_instances(self):
        c1 = InstaparserClient(api_key="key1", base_url="https://api1.com")
        c2 = InstaparserClient(api_key="key2", base_url="https://api2.com")
        assert c1.api_key != c2.api_key
        assert c1.base_url != c2.base_url

    def test_client_reuse(self, client, mock_request):
        mock_request.return_value = make_response(json_data=ARTICLE_DATA)
        a1 = client.Article(url="u1")
        a2 = client.Article(url="u2")
        assert mock_request.call_count == 2
        assert a1.title == a2.title == "Test Article Title"


class TestErrorPropagation:
    @pytest.mark.parametrize("status, exc_cls", ERROR_CODES)
    def test_article_errors(self, client, mock_request, status, exc_cls):
        mock_request.side_effect = make_error(status, json_data={"reason": f"Error {status}"})
        with pytest.raises(exc_cls) as exc_info:
            client.Article(url="u")
        assert exc_info.value.status_code == status

    @pytest.mark.parametrize("status, exc_cls", ERROR_CODES)
    def test_summary_errors(self, client, mock_request, status, exc_cls):
        mock_request.side_effect = make_error(status, json_data={"reason": f"Error {status}"})
        with pytest.raises(exc_cls):
            client.Summary(url="u")

    @pytest.mark.parametrize("status, exc_cls", ERROR_CODES)
    def test_pdf_errors(self, client, mock_request, status, exc_cls):
        mock_request.side_effect = make_error(status, json_data={"reason": f"Error {status}"})
        with pytest.raises(exc_cls):
            client.PDF(url="u")

    def test_error_without_reason_field(self, client, mock_request):
        mock_request.side_effect = make_error(500, json_data={})
        with pytest.raises(InstaparserAPIError, match="API request failed"):
            client.Article(url="u")

    def test_error_plain_text_body(self, client, mock_request):
        mock_request.side_effect = make_error(500, text="Error message")
        with pytest.raises(InstaparserAPIError, match="Error message"):
            client.Article(url="u")

    def test_error_empty_body(self, client, mock_request):
        mock_request.side_effect = make_error(500, text="")
        with pytest.raises(InstaparserAPIError) as exc_info:
            client.Article(url="u")
        assert exc_info.value.status_code == 500


class TestOutputFormats:
    @pytest.mark.parametrize(
        "output, field, body_text",
        [
            ("html", "html", "<p>HTML content</p>"),
            ("text", "text", "Text content"),
            ("markdown", "markdown", "# Markdown content"),
        ],
    )
    def test_article_output_formats(self, client, mock_request, output, field, body_text):
        mock_request.return_value = make_response(json_data={"url": "u", field: body_text})
        article = client.Article(url="u", output=output)
        assert article.body == body_text

    @pytest.mark.parametrize(
        "output, field, body_text",
        [
            ("html", "html", "<p>PDF HTML</p>"),
            ("text", "text", "PDF Text"),
            ("markdown", "markdown", "# PDF markdown"),
        ],
    )
    def test_pdf_output_formats(self, client, mock_request, output, field, body_text):
        mock_request.return_value = make_response(json_data={"url": "u", field: body_text})
        pdf = client.PDF(url="u", output=output)
        assert pdf.body == body_text


class TestEncodeMultipartFormdata:
    def test_fields_only(self):
        body, content_type = _encode_multipart_formdata({"key": "value"}, {})
        assert content_type.startswith("multipart/form-data; boundary=")
        assert b'name="key"' in body
        assert b"value" in body
        assert body.endswith(b"--\r\n")

    def test_file_from_bytes(self):
        body, content_type = _encode_multipart_formdata({}, {"file": b"PDF content"})
        assert b'name="file"' in body
        assert b'filename="upload"' in body
        assert b"application/octet-stream" in body
        assert b"PDF content" in body

    def test_file_from_file_object(self):
        f = io.BytesIO(b"file data")
        body, _ = _encode_multipart_formdata({}, {"file": f})
        assert b"file data" in body

    def test_fields_and_files(self):
        body, content_type = _encode_multipart_formdata(
            {"output": "html", "use_cache": "false"},
            {"file": b"data"},
        )
        boundary = content_type.split("boundary=")[1]
        parts = body.split(f"--{boundary}".encode())
        # parts: ['', field1, field2, file, '--\r\n']
        assert len(parts) == 5
        assert b'name="output"' in parts[1]
        assert b'name="use_cache"' in parts[2]
        assert b'name="file"' in parts[3]

    def test_boundary_is_unique(self):
        _, ct1 = _encode_multipart_formdata({}, {})
        _, ct2 = _encode_multipart_formdata({}, {})
        assert ct1 != ct2
