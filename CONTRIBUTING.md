# Contributing

## Setup

Requires Python 3.10 or later.

```sh
pip install -e . --group dev
```

## Running Tests

```sh
pytest

# With coverage:
pytest --cov=instaparser
```

## Linting & Type Checking

```sh
ruff check instaparser/ tests/
ruff format --check instaparser/ tests/
mypy
```

## Versioning

The package version is defined in `instaparser/__init__.py` and read by setuptools at build time via `[tool.setuptools.dynamic]` in `pyproject.toml`.
