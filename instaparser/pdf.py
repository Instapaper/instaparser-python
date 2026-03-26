"""
PDF class representing a parsed PDF from Instaparser.
"""

from typing import Any

from .article import Article


class PDF(Article):
    """
    Represents a parsed PDF from Instaparser.

    Inherits from Article since most fields are the same.
    PDFs always have is_rtl=False and videos=[].
    """

    def __init__(self, data: dict[str, Any]):
        """
        Initialize a PDF from API response data.

        Args:
            data: Dictionary containing PDF data from the API
        """
        # Call parent constructor
        super().__init__(data)

        # PDFs always have is_rtl=False and videos=[]
        self.is_rtl = False
        self.videos = []

    def __repr__(self) -> str:
        return f"<PDF url={self.url!r} title={self.title!r}>"
