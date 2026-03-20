"""
Article class representing a parsed article from Instaparser.
"""

from typing import Any


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
    
    def __init__(self, data: dict[str, Any]):
        """
        Initialize an Article from API response data.
        
        Args:
            data: Dictionary containing article data from the API
        """
        self.url = data.get('url')
        self.title = data.get('title')
        self.site_name = data.get('site_name')
        self.author = data.get('author')
        self.date = data.get('date')
        self.description = data.get('description')
        self.thumbnail = data.get('thumbnail')
        self.words = data.get('words', 0)
        self.is_rtl = data.get('is_rtl', False)
        self.images = data.get('images', [])
        self.videos = data.get('videos', [])
        
        self.html = data.get('html')
        self.text = data.get('text')
        self.markdown = data.get('markdown')
        
        self.body = self.html or self.text or self.markdown
    
    def __repr__(self) -> str:
        return f"<Article url={self.url!r} title={self.title!r}>"
    
    def __str__(self) -> str:
        return self.body or ""
