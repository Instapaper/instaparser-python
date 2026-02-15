"""
InstaparserClient - Main client class for the Instaparser API.
"""

import json
from collections.abc import Callable
from typing import Any, BinaryIO
from urllib.parse import urljoin

import requests

from .article import Article
from .exceptions import (
    InstaparserAPIError,
    InstaparserAuthenticationError,
    InstaparserRateLimitError,
    InstaparserValidationError,
)
from .pdf import PDF
from .summary import Summary


class InstaparserClient:
    """
    Client for interacting with the Instaparser API.

    Example:
        >>> client = InstaparserClient(api_key="your-api-key")
        >>> article = client.Article(url="https://example.com/article")
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
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }
        )

    def _handle_response(self, response: requests.Response) -> dict[str, Any]:
        """
        Handle API response and raise appropriate exceptions.

        Args:
            response: The HTTP response object

        Returns:
            Parsed JSON response data

        Raises:
            InstaparserAuthenticationError: For 401 errors
            InstaparserRateLimitError: For 429 errors
            InstaparserValidationError: For 400 errors
            InstaparserAPIError: For other API errors
        """
        status_code = response.status_code

        if status_code == 200:
            try:
                parsed = response.json()
                if isinstance(parsed, dict):
                    return parsed
            except ValueError:
                # Some endpoints might return non-JSON
                return {"raw": response.text}

        error_message = f"API request failed with status {status_code}"
        try:
            error_data = response.json()
            if isinstance(error_data, dict) and "reason" in error_data:
                error_message = error_data["reason"]
        except ValueError:
            error_message = response.text or error_message

        if status_code == 401:
            raise InstaparserAuthenticationError(
                error_message or "Invalid API key", status_code=status_code, response=response
            )
        elif status_code == 403:
            raise InstaparserAPIError(error_message or "Account suspended", status_code=status_code, response=response)
        elif status_code == 409:
            raise InstaparserAPIError(
                error_message or "Exceeded monthly API calls", status_code=status_code, response=response
            )
        elif status_code == 429:
            raise InstaparserRateLimitError(
                error_message or "Rate limit exceeded", status_code=status_code, response=response
            )
        elif status_code == 400:
            raise InstaparserValidationError(
                error_message or "Invalid request", status_code=status_code, response=response
            )
        else:
            raise InstaparserAPIError(error_message, status_code=status_code, response=response)

    def Article(self, url: str, content: str | None = None, output: str = "html", use_cache: bool = True) -> Article:
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
            >>> article = client.Article(url="https://example.com/article")
            >>> print(article.title)
            >>> print(article.body)
        """
        if output not in ("html", "text", "markdown"):
            raise InstaparserValidationError("output must be 'html', 'text', or 'markdown'")

        endpoint = urljoin(self.base_url, "/api/1/article")
        payload = {
            "url": url,
            "output": output,
        }
        # API expects string 'false' to disable cache, not boolean False
        if not use_cache:
            payload["use_cache"] = "false"

        if content is not None:
            payload["content"] = content

        response = self.session.post(endpoint, json=payload)
        data = self._handle_response(response)
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

    def Summary(
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
            >>> summary = client.Summary(url="https://example.com/article")
            >>> print(summary.overview)
            >>> print(summary.key_sentences)

            >>> # With streaming callback
            >>> def on_line(line):
            ...     print(f"Received: {line}")
            >>> summary = client.Summary(url="https://example.com/article", stream_callback=on_line)
        """
        endpoint = urljoin(self.base_url, "/api/1/summary")
        payload = {
            "url": url,
            "stream": stream_callback is not None,
        }
        # API expects string 'false' to disable cache, not boolean False
        if not use_cache:
            payload["use_cache"] = "false"

        if content is not None:
            payload["content"] = content

        if stream_callback is not None:
            # Handle streaming response
            response = self.session.post(endpoint, json=payload, stream=True)
            if response.status_code != 200:
                self._handle_response(response)

            key_sentences = []
            overview = ""
            for line in response.iter_lines():
                if line:
                    line_str = line.decode("utf-8")
                    # Call the callback for each line
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
            response = self.session.post(endpoint, json=payload)
            data = self._handle_response(response)
            return Summary(key_sentences=data.get("key_sentences", []), overview=data.get("overview", ""))

    def PDF(
        self, url: str | None = None, file: BinaryIO | bytes | None = None, output: str = "html", use_cache: bool = True
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
            >>> pdf = client.PDF(url="https://example.com/document.pdf")

            >>> # Parse PDF from file
            >>> with open('document.pdf', 'rb') as f:
            ...     pdf = client.PDF(file=f)
        """
        if output not in ("html", "text", "markdown"):
            raise InstaparserValidationError("output must be 'html', 'text', or 'markdown'")

        endpoint = urljoin(self.base_url, "/api/1/pdf")

        if file is not None:
            # POST request with file upload
            files = {"file": file}
            data = {
                "output": output,
            }
            # API expects string 'false' to disable cache, not boolean False
            if not use_cache:
                data["use_cache"] = "false"
            if url:
                data["url"] = url

            # Remove Content-Type header for multipart/form-data
            headers = {k: v for k, v in self.session.headers.items() if k != "Content-Type"}
            response = self.session.post(endpoint, files=files, data=data, headers=headers)
        elif url:
            # GET request with URL
            params = {
                "url": url,
                "output": output,
            }
            # API expects string 'false' to disable cache, not boolean False
            if not use_cache:
                params["use_cache"] = "false"
            response = self.session.get(endpoint, params=params)
        else:
            raise InstaparserValidationError("Either 'url' or 'file' must be provided")

        result = self._handle_response(response)
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
