#!/usr/bin/env python
"""
Example usage of the Instaparser Python Library.

Run a single API call (article, pdf, or summary) with options via argparse.
API token can be passed via --api-key or INSTAPARSER_API_KEY environment variable.
"""

import argparse
import os
import sys

from instaparser import (
    InstaparserAPIError,
    InstaparserAuthenticationError,
    InstaparserClient,
    InstaparserRateLimitError,
    InstaparserValidationError,
)


def get_api_key(args: argparse.Namespace) -> str:
    """Resolve API key from argument or environment."""
    key = getattr(args, "api_key", None) or os.environ.get("INSTAPARSER_API_KEY")
    if not key:
        print("Error: API key required. Use --api-key or set INSTAPARSER_API_KEY.", file=sys.stderr)
        sys.exit(1)
    return key


def cmd_article(client: InstaparserClient, args: argparse.Namespace) -> None:
    """Call Article API and print result."""
    article = client.Article(
        url=args.url,
        output=args.output,
        use_cache=not args.no_cache,
    )
    print(f"Title: {article.title}")
    print(f"Author: {article.author}")
    print(f"Words: {article.words}")
    if args.output == "text" and article.text:
        print(f"Body (first 400 chars): {article.text[:400]}...")
    elif article.body:
        print(f"Body (first 400 chars): {article.body[:400]}...")
    else:
        print("Body: (none)")


def cmd_summary(client: InstaparserClient, args: argparse.Namespace) -> None:
    """Call Summary API and print result."""

    def on_stream(line: str) -> None:
        if args.stream:
            print(f"  {line}")

    summary = client.Summary(
        url=args.url,
        use_cache=not args.no_cache,
        stream_callback=on_stream if args.stream else None,
    )
    print(f"Overview: {summary.overview}")
    print("Key sentences:")
    for s in summary.key_sentences:
        print(f"  - {s}")


def cmd_pdf(client: InstaparserClient, args: argparse.Namespace) -> None:
    """Call PDF API and print result."""
    if args.file:
        with open(args.file, "rb") as f:
            pdf = client.PDF(
                file=f,
                url=args.url or None,
                output=args.output,
                use_cache=not args.no_cache,
            )
    else:
        if not args.url:
            print("Error: --url or --file required for pdf.", file=sys.stderr)
            sys.exit(1)
        pdf = client.PDF(
            url=args.url,
            output=args.output,
            use_cache=not args.no_cache,
        )
    print(f"Title: {pdf.title}")
    print(f"Words: {pdf.words}")
    body = pdf.body or pdf.text or ""
    print(f"Body (first 400 chars): {body[:400]}..." if body else "Body: (none)")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Instaparser API: run one API call (article, pdf, or summary).",
    )
    parser.add_argument(
        "--api-key",
        default=os.environ.get("INSTAPARSER_API_KEY"),
        help="API key (default: INSTAPARSER_API_KEY env var)",
    )
    subparsers = parser.add_subparsers(dest="command", required=True, help="API to call")

    # article
    article_parser = subparsers.add_parser("article", help="Parse article from URL")
    article_parser.add_argument("url", help="Article URL")
    article_parser.add_argument(
        "--output",
        choices=("html", "text", "markdown"),
        default="html",
        help="Output format (default: html)",
    )
    article_parser.add_argument("--no-cache", action="store_true", help="Disable cache")

    # summary
    summary_parser = subparsers.add_parser("summary", help="Summarize article from URL")
    summary_parser.add_argument("url", help="Article URL")
    summary_parser.add_argument("--no-cache", action="store_true", help="Disable cache")
    summary_parser.add_argument(
        "--stream",
        action="store_true",
        help="Stream summary output line by line",
    )

    # pdf
    pdf_parser = subparsers.add_parser("pdf", help="Parse PDF from URL or file")
    pdf_parser.add_argument("--url", help="PDF URL")
    pdf_parser.add_argument("--file", help="Path to PDF file (alternative to --url)")
    pdf_parser.add_argument(
        "--output",
        choices=("html", "text", "markdown"),
        default="html",
        help="Output format (default: html)",
    )
    pdf_parser.add_argument("--no-cache", action="store_true", help="Disable cache")

    args = parser.parse_args()
    api_key = get_api_key(args)

    client = InstaparserClient(api_key=api_key)

    try:
        if args.command == "article":
            cmd_article(client, args)
        elif args.command == "summary":
            cmd_summary(client, args)
        elif args.command == "pdf":
            cmd_pdf(client, args)
    except InstaparserAuthenticationError:
        print("Authentication failed - check your API key", file=sys.stderr)
        sys.exit(1)
    except InstaparserRateLimitError:
        print("Rate limit exceeded - slow down your requests", file=sys.stderr)
        sys.exit(1)
    except InstaparserValidationError as e:
        print(f"Validation error: {e}", file=sys.stderr)
        sys.exit(1)
    except InstaparserAPIError as e:
        print(f"API error: {e} (status: {e.status_code})", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
