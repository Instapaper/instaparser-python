"""Model classes representing parsed results from Instaparser."""

from dataclasses import dataclass, field
from typing import Any


@dataclass(repr=False)
class Article:
    """
    Represents a parsed article from Instaparser.

    Attributes:
        url: The canonical URL of the article
        title: The title of the article
        site_name: The name of the website
        author: The author's name
        date: Published date as UNIX timestamp
        description: Article description
        thumbnail: Thumbnail image URL
        words: Number of words in the article
        is_rtl: Whether the article is right-to-left (Arabic/Hebrew)
        images: List of images in the article
        videos: List of embedded videos
        body: The article body (HTML, text, or markdown depending on output format)
        html: The HTML body (if output was 'html')
        text: The plain text body (if output was 'text')
        markdown: The markdown body (if output was 'markdown')
    """

    url: str | None = None
    title: str | None = None
    site_name: str | None = None
    author: str | None = None
    date: Any | None = None
    description: str | None = None
    thumbnail: str | None = None
    words: int = 0
    is_rtl: bool = False
    images: list[str] = field(default_factory=list)
    videos: list[str] = field(default_factory=list)
    html: str | None = None
    text: str | None = None
    markdown: str | None = None

    @property
    def body(self) -> str | None:
        """The article body (html if available, otherwise text, then markdown)."""
        return self.html or self.text or self.markdown

    def __repr__(self) -> str:
        return f"<Article url={self.url!r} title={self.title!r}>"

    def __str__(self) -> str:
        return self.body or ""


@dataclass(repr=False)
class PDF(Article):
    """
    Represents a parsed PDF from Instaparser.

    Inherits from Article since most fields are the same.
    PDFs always have is_rtl=False and videos=[].
    """

    def __post_init__(self) -> None:
        self.is_rtl = False
        self.videos = []

    def __repr__(self) -> str:
        return f"<PDF url={self.url!r} title={self.title!r}>"


@dataclass(repr=False)
class Summary:
    """
    Represents a summary result from Instaparser.

    Attributes:
        key_sentences: List of key sentences extracted from the article
        overview: Concise summary of the article
    """

    key_sentences: list[str]
    overview: str

    def __repr__(self) -> str:
        overview = self.overview[:50] + "..." if len(self.overview) > 50 else self.overview
        return f"<Summary overview={overview!r} key_sentences={len(self.key_sentences)}>"

    def __str__(self) -> str:
        return self.overview
