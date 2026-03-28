"""
PDF class representing a parsed PDF from Instaparser.
"""

from dataclasses import dataclass

from .article import Article


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
