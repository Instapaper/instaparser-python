"""
Summary class representing a summary result from Instaparser.
"""


class Summary:
    """
    Represents a summary result from Instaparser.

    Attributes:
        key_sentences: List of key sentences extracted from the article
        overview: Concise summary of the article
    """

    def __init__(self, key_sentences: list[str], overview: str):
        """
        Initialize a Summary from API response data.

        Args:
            key_sentences: List of key sentences extracted from the article
            overview: Concise summary of the article
        """
        self.key_sentences = key_sentences
        self.overview = overview

    def __repr__(self) -> str:
        return f"<Summary overview={self.overview[:50]!r}... key_sentences={len(self.key_sentences)}>"

    def __str__(self) -> str:
        return self.overview
