# Instaparser Python Library

A Python client library for the [Instaparser API](https://instaparser.com), providing a simple and intuitive interface for parsing articles, generating summaries, and processing PDFs.

## Installation

```bash
pip install instaparser
```

## Quick Start

```python
from instaparser import InstaparserClient

# Initialize the client with your API key
client = InstaparserClient(api_key="your-api-key")

# Parse an article from a URL
article = client.article(url="https://example.com/article")

# Access article properties
print(article.title)
print(article.body)  # HTML or text content
print(article.author)
print(article.words)
```

## Features

- **Article Parsing**: Extract clean HTML, text, or markdown from web articles
- **Summary Generation**: Generate AI-powered summaries with key sentences
- **PDF Processing**: Parse PDFs from URLs or file uploads
- **Error Handling**: Comprehensive exception handling for API errors
- **Type Hints**: Full type annotations for better IDE support

## Usage

### Article Parsing

Parse articles from URLs or HTML content:

```python
from instaparser import InstaparserClient

client = InstaparserClient(api_key="your-api-key")

# Parse from URL (HTML output)
article = client.article(url="https://example.com/article")
print(article.html)  # HTML content
print(article.body)  # Same as html when output='html'

# Parse from URL (text output)
article = client.article(url="https://example.com/article", output="text")
print(article.text)  # Plain text content
print(article.body)  # Same as text when output='text'

# Parse from URL (markdown output)
article = client.article(url="https://example.com/article", output="markdown")
print(article.markdown)  # Markdown content
print(article.body)      # Same as markdown when output='markdown'

# Parse from HTML content
html_content = "<html><body><h1>Title</h1><p>Content</p></body></html>"
article = client.article(url="https://example.com/article", content=html_content)

# Disable cache
article = client.article(url="https://example.com/article", use_cache=False)
```

### Article Properties

The `Article` object provides access to all parsed metadata:

```python
article = client.article(url="https://example.com/article")

# Basic properties
article.url          # Canonical URL
article.title        # Article title
article.site_name    # Website name
article.author       # Author name
article.date         # Published date (UNIX timestamp)
article.description  # Article description
article.thumbnail    # Thumbnail image URL
article.words        # Word count
article.is_rtl       # Right-to-left language flag

# Content
article.body         # HTML, text, or markdown (depending on output format)
article.html         # HTML content (if output='html')
article.text         # Plain text (if output='text')
article.markdown     # Markdown content (if output='markdown')

# Media
article.images       # List of images
article.videos       # List of embedded videos
```

### Summary Generation

Generate AI-powered summaries:

```python
# Generate summary
summary = client.summary(url="https://example.com/article")

print(summary.overview)        # Concise summary
print(summary.key_sentences)   # List of key sentences

# Stream summary with callback (for real-time updates)
def on_stream_line(line):
    print(f"Streaming: {line}")

summary = client.summary(
    url="https://example.com/article",
    stream_callback=on_stream_line
)
```

### PDF Processing

Parse PDFs from URLs or files. The PDF class inherits from Article, so it has all the same properties:

```python
# Parse PDF from URL
pdf = client.pdf(url="https://example.com/document.pdf")

# Parse PDF from file
with open('document.pdf', 'rb') as f:
    pdf = client.pdf(file=f)

# Parse PDF with text output
pdf = client.pdf(url="https://example.com/document.pdf", output="text")
print(pdf.text)
print(pdf.body)  # Same as text when output='text'

# Parse PDF with markdown output
pdf = client.pdf(url="https://example.com/document.pdf", output="markdown")
print(pdf.markdown)
print(pdf.body)  # Same as markdown when output='markdown'

# Access all Article properties
print(pdf.title)
print(pdf.words)
print(pdf.images)
```

## Error Handling

The SDK provides specific exception types for different error scenarios:

```python
from instaparser import (
    InstaparserClient,
    InstaparserAuthenticationError,
    InstaparserRateLimitError,
    InstaparserValidationError,
    InstaparserAPIError,
)

client = InstaparserClient(api_key="your-api-key")

try:
    article = client.article(url="https://example.com/article")
except InstaparserAuthenticationError:
    print("Invalid API key")
except InstaparserRateLimitError:
    print("Rate limit exceeded")
except InstaparserValidationError:
    print("Invalid request parameters")
except InstaparserAPIError as e:
    print(f"API error: {e} (status: {e.status_code})")
```

## API Reference

### InstaparserClient

Main client class for interacting with the Instaparser API.

#### `__init__(api_key: str, base_url: str | None = None, timeout: float | None = 60)`

Initialize the client.

- `api_key`: Your Instaparser API key
- `base_url`: Optional override for the API base URL
- `timeout`: Connection timeout in seconds (default: `60`; pass `None` to disable)

#### `article(url: str, content: Optional[str] = None, output: str = 'html', use_cache: bool = True) -> Article`

Parse an article from a URL or HTML content.

- `url`: URL of the article (required)
- `content`: Optional HTML content to parse instead of fetching from URL
- `output`: Output format - `'html'` (default), `'text'`, or `'markdown'`
- `use_cache`: Whether to use cache (default: `True`)

Returns: `Article` object

#### `summary(url: str, content: Optional[str] = None, use_cache: bool = True, stream_callback: Optional[Callable[[str], None]] = None) -> Summary`

Generate a summary of an article.

- `url`: URL of the article (required)
- `content`: Optional HTML content to parse instead of fetching from URL
- `use_cache`: Whether to use cache (default: `True`)
- `stream_callback`: Optional callback function called for each line of streaming response. If provided, enables streaming mode.

Returns: `Summary` object with `key_sentences` and `overview` attributes

#### `pdf(url: Optional[str] = None, file: Optional[Union[BinaryIO, bytes]] = None, output: str = 'html', use_cache: bool = True) -> PDF`

Parse a PDF from a URL or file.

- `url`: URL of the PDF (required for GET request)
- `file`: PDF file to upload (required for POST request)
- `output`: Output format - `'html'` (default), `'text'`, or `'markdown'`
- `use_cache`: Whether to use cache (default: `True`)

Returns: `PDF` object (inherits from `Article`)

### Article

Represents a parsed article from Instaparser.

#### Properties

- `url`: Canonical URL
- `title`: Article title
- `site_name`: Website name
- `author`: Author name
- `date`: Published date (UNIX timestamp)
- `description`: Article description
- `thumbnail`: Thumbnail image URL
- `words`: Word count
- `is_rtl`: Right-to-left language flag
- `images`: List of images
- `videos`: List of embedded videos
- `body`: Article body (HTML, text, or markdown)
- `html`: HTML content (if output was 'html')
- `text`: Plain text content (if output was 'text')
- `markdown`: Markdown content (if output was 'markdown')

### PDF

Represents a parsed PDF from Instaparser. Inherits from `Article` and has all the same properties. PDFs always have `is_rtl=False` and `videos=[]`.

### Summary

Represents a summary result from Instaparser.

#### Properties

- `key_sentences`: List of key sentences extracted from the article
- `overview`: Concise summary of the article

## License

MIT

## Support

For support, email support@instaparser.com or visit [https://instaparser.com](https://instaparser.com).
