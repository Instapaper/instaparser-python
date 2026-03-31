"""
InstaparserClient - Main client class for the Instaparser API.
"""

import json
import uuid
import warnings
from collections.abc import Callable
from http.client import HTTPResponse
from typing import Any, BinaryIO, NoReturn
from urllib.error import HTTPError
from urllib.parse import urlencode, urljoin
from urllib.request import Request, urlopen

from .article import Article
from .exceptions import (
    InstaparserAPIError,
    InstaparserAuthenticationError,
    InstaparserRateLimitError,
    InstaparserValidationError,
)
from .pdf import PDF
from .summary import Summary


def _encode_multipart_formdata(
    fields: dict[str, str],
    files: dict[str, BinaryIO | bytes],
) -> tuple[bytes, str]:
    """
    Encode fields and files as multipart/form-data.

    Args:
        fields: Dictionary of form field name/value pairs
        files: Dictionary of file field name to file-like object or bytes

    Returns:
        Tuple of (encoded body bytes, content-type header value)
    """
    boundary = uuid.uuid4().hex
    lines: list[bytes] = []

    for name, value in fields.items():
        lines.append(f"--{boundary}\r\n".encode())
        lines.append(f'Content-Disposition: form-data; name="{name}"\r\n'.encode())
        lines.append(b"\r\n")
        lines.append(f"{value}\r\n".encode())

    for name, file_data in files.items():
        if hasattr(file_data, "read"):
            data = file_data.read()
        else:
            data = file_data
        lines.append(f"--{boundary}\r\n".encode())
        lines.append(f'Content-Disposition: form-data; name="{name}"; filename="upload"\r\n'.encode())
        lines.append(b"Content-Type: application/octet-stream\r\n")
        lines.append(b"\r\n")
        lines.append(data)
        lines.append(b"\r\n")

    lines.append(f"--{boundary}--\r\n".encode())

    body = b"".join(lines)
    content_type = f"multipart/form-data; boundary={boundary}"
    return body, content_type


def _map_http_error(e: HTTPError) -> NoReturn:
    """
    Translate an HTTPError into the appropriate Instaparser domain exception.

    Reads the response body from the HTTPError, extracts the ``reason``
    field from the JSON payload (if present), and raises the matching
    Instaparser exception.
    """
    status_code = e.code

    body = e.read().decode("utf-8")
    error_message = f"API request failed with status {status_code}"
    try:
        error_data = json.loads(body)
        if isinstance(error_data, dict) and "reason" in error_data:
            error_message = error_data["reason"]
    except (ValueError, json.JSONDecodeError):
        error_message = body or error_message

    errors: dict[int, tuple[type[InstaparserAPIError], str]] = {
        400: (InstaparserValidationError, "Invalid request"),
        401: (InstaparserAuthenticationError, "Invalid API key"),
        403: (InstaparserAPIError, "Account suspended"),
        409: (InstaparserAPIError, "Exceeded monthly API calls"),
        429: (InstaparserRateLimitError, "Rate limit exceeded"),
    }

    exc_cls, default_msg = errors.get(status_code, (InstaparserAPIError, ""))
    raise exc_cls(error_message or default_msg, status_code=status_code, response=e)


class InstaparserClient:
    """
    Client for interacting with the Instaparser API.

    Example:
        >>> client = InstaparserClient(api_key="your-api-key")
        >>> article = client.article(url="https://example.com/article")
        >>> print(article.body)
    """

    BASE_URL = "https://instaparser.com"

    def __init__(self, api_key: str, base_url: str | None = None):
        """
        Initialize the Instaparser client.

        Args:
            api_key: Your Instaparser API key
            base_url: Optional base URL for the API (defaults to production)
        """
        self.api_key = api_key
        self.base_url = base_url or self.BASE_URL
        self.headers = {
            "Authorization": f"Bearer {api_key}",
        }

    def __repr__(self) -> str:
        return f"<InstaparserClient base_url={self.base_url!r}>"

    def _request(
        self,
        method: str,
        path: str,
        *,
        json_data: dict | None = None,
        params: dict | None = None,
        multipart_fields: dict[str, str] | None = None,
        multipart_files: dict[str, BinaryIO | bytes] | None = None,
    ) -> HTTPResponse:
        """
        Make an HTTP request using urllib.

        Args:
            method: HTTP method (GET, POST)
            path: API endpoint path (e.g. "/api/1/article")
            json_data: JSON body payload
            params: Query parameters
            multipart_fields: Form fields for multipart upload
            multipart_files: Files for multipart upload

        Returns:
            HTTPResponse on success

        Raises:
            HTTPError: On non-2xx status codes (callers convert via _map_http_error)
        """
        url = urljoin(self.base_url, path)
        if params:
            url = f"{url}?{urlencode(params)}"

        data = None
        headers = self.headers.copy()

        if multipart_fields or multipart_files:
            data, content_type = _encode_multipart_formdata(multipart_fields or {}, multipart_files or {})
            headers["Content-Type"] = content_type
        elif json_data is not None:
            data = json.dumps(json_data).encode("utf-8")
            headers["Content-Type"] = "application/json"

        req = Request(url, data=data, headers=headers, method=method)
        response: HTTPResponse = urlopen(req)
        return response

    def _read_json(self, response: HTTPResponse) -> dict[str, Any]:
        """
        Read and parse a successful JSON response.

        Returns:
            Parsed JSON dict, or ``{"raw": text}`` if the body isn't valid JSON.
        """
        body = response.read().decode("utf-8")
        try:
            parsed = json.loads(body)
            if isinstance(parsed, dict):
                return parsed
        except (ValueError, json.JSONDecodeError):
            pass
        return {"raw": body}

    def article(self, url: str, content: str | None = None, output: str = "html", use_cache: bool = True) -> Article:
        """
        Parse an article from a URL or HTML content.

        Args:
            url: URL of the article to parse (required)
            content: Optional raw HTML content to parse instead of fetching from URL
            output: Output format - 'html' (default), 'text', or 'markdown'
            use_cache: Whether to use cache (default: True)

        Returns:
            Article object with parsed content

        Example:
            >>> article = client.article(url="https://example.com/article")
            >>> print(article.title)
            >>> print(article.body)
        """
        if output not in ("html", "text", "markdown"):
            raise InstaparserValidationError("output must be 'html', 'text', or 'markdown'")

        payload: dict[str, Any] = {
            "url": url,
            "output": output,
        }
        if not use_cache:
            payload["use_cache"] = "false"
        if content is not None:
            payload["content"] = content

        try:
            response = self._request("POST", "/api/1/article", json_data=payload)
        except HTTPError as e:
            _map_http_error(e)

        data = self._read_json(response)
        return Article(
            url=data.get("url"),
            title=data.get("title"),
            site_name=data.get("site_name"),
            author=data.get("author"),
            date=data.get("date"),
            description=data.get("description"),
            thumbnail=data.get("thumbnail"),
            words=data.get("words", 0),
            is_rtl=data.get("is_rtl", False),
            images=data.get("images", []),
            videos=data.get("videos", []),
            html=data.get("html"),
            text=data.get("text"),
            markdown=data.get("markdown"),
        )

    def summary(
        self,
        url: str,
        content: str | None = None,
        use_cache: bool = True,
        stream_callback: Callable[[str], None] | None = None,
    ) -> Summary:
        """
        Generate a summary of an article.

        Args:
            url: URL of the article to summarize (required)
            content: Optional HTML content to parse instead of fetching from URL
            use_cache: Whether to use cache (default: True)
            stream_callback: Optional callback function called for each line of streaming response.
                           If provided, enables streaming mode. The callback receives each line as a string.

        Returns:
            Summary object with key_sentences and overview attributes

        Example:
            >>> summary = client.summary(url="https://example.com/article")
            >>> print(summary.overview)
            >>> print(summary.key_sentences)

            >>> # With streaming callback
            >>> def on_line(line):
            ...     print(f"Received: {line}")
            >>> summary = client.summary(url="https://example.com/article", stream_callback=on_line)
        """
        payload: dict[str, Any] = {
            "url": url,
            "stream": stream_callback is not None,
        }
        if not use_cache:
            payload["use_cache"] = "false"
        if content is not None:
            payload["content"] = content

        try:
            response = self._request("POST", "/api/1/summary", json_data=payload)
        except HTTPError as e:
            _map_http_error(e)

        if stream_callback is not None:
            key_sentences: list[str] = []
            overview = ""
            for raw_line in response:
                line = raw_line.strip(b"\r\n")
                if line:
                    line_str = line.decode("utf-8")
                    stream_callback(line_str)

                    if line_str.startswith("key_sentences:"):
                        try:
                            key_sentences = json.loads(line_str.split(":", 1)[1].strip())
                        except json.JSONDecodeError:
                            raise InstaparserAPIError("Unable to generate key sentences", status_code=412)
                    elif line_str.startswith("delta:"):
                        delta_content = line_str.split(": ", 1)[1]
                        overview += delta_content

            return Summary(key_sentences=key_sentences, overview=overview)
        else:
            data = self._read_json(response)
            return Summary(key_sentences=data.get("key_sentences", []), overview=data.get("overview", ""))

    def pdf(
        self,
        url: str | None = None,
        file: BinaryIO | bytes | None = None,
        output: str = "html",
        use_cache: bool = True,
    ) -> PDF:
        """
        Parse a PDF from a URL or file.

        Args:
            url: URL of the PDF to parse (required for GET request)
            file: PDF file to upload (required for POST request, can be file-like object or bytes)
            output: Output format - 'html' (default), 'text', or 'markdown'
            use_cache: Whether to use cache (default: True)

        Returns:
            PDF object with parsed PDF content (inherits from Article)

        Example:
            >>> # Parse PDF from URL
            >>> pdf = client.pdf(url="https://example.com/document.pdf")

            >>> # Parse PDF from file
            >>> with open('document.pdf', 'rb') as f:
            ...     pdf = client.pdf(file=f)
        """
        if output not in ("html", "text", "markdown"):
            raise InstaparserValidationError("output must be 'html', 'text', or 'markdown'")

        if file is not None:
            fields = {"output": output}
            if not use_cache:
                fields["use_cache"] = "false"
            if url:
                fields["url"] = url

            try:
                response = self._request(
                    "POST",
                    "/api/1/pdf",
                    multipart_fields=fields,
                    multipart_files={"file": file},
                )
            except HTTPError as e:
                _map_http_error(e)
        elif url:
            params = {
                "url": url,
                "output": output,
            }
            if not use_cache:
                params["use_cache"] = "false"

            try:
                response = self._request("GET", "/api/1/pdf", params=params)
            except HTTPError as e:
                _map_http_error(e)
        else:
            raise InstaparserValidationError("Either 'url' or 'file' must be provided")

        result = self._read_json(response)
        return PDF(
            url=result.get("url"),
            title=result.get("title"),
            site_name=result.get("site_name"),
            author=result.get("author"),
            date=result.get("date"),
            description=result.get("description"),
            thumbnail=result.get("thumbnail"),
            words=result.get("words", 0),
            images=result.get("images", []),
            html=result.get("html"),
            text=result.get("text"),
            markdown=result.get("markdown"),
        )

    # Deprecated aliases for backwards compatibility:

    def Article(self, *args: Any, **kwargs: Any) -> Article:  # noqa: N802
        """Deprecated: use client.article() instead."""
        warnings.warn(
            "client.Article() is deprecated, use client.article() instead",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.article(*args, **kwargs)

    def PDF(self, *args: Any, **kwargs: Any) -> PDF:  # noqa: N802
        """Deprecated: use client.pdf() instead."""
        warnings.warn(
            "client.PDF() is deprecated, use client.pdf() instead",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.pdf(*args, **kwargs)

    def Summary(self, *args: Any, **kwargs: Any) -> Summary:  # noqa: N802
        """Deprecated: use client.summary() instead."""
        warnings.warn(
            "client.Summary() is deprecated, use client.summary() instead",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.summary(*args, **kwargs)
