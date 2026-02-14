# Build Instructions

## Prerequisites

- Python 3.10 or later
- pip

## Setup

Install the runtime and build dependencies:

```sh
pip install -e .
```

For development (linting, type-checking, testing), also install the dev extras:

```sh
pip install -e . --group dev
```

For builds and deploys , also install the build extras:

```sh
pip install -e . --group build
```

## Running Tests

```sh
pytest
```

With coverage:

```sh
pytest --cov=instaparser
```

## Linting & Type Checking

```sh
ruff check instaparser/
ruff format --check instaparser/
mypy instaparser/
```

## Building the Package

Build both the sdist and wheel:

```sh
python -m build
```

The outputs will be in the `dist/` directory.

## Publishing to PyPI

Upload the built artifacts with twine:

```sh
twine upload dist/*
```

To test against Test PyPI first:

```sh
twine upload --repository testpypi dist/*
```

## Versioning

The package version is defined in `instaparser/__init__.py` and read automatically by Hatch at build time via the `[tool.hatch.version]` configuration in `pyproject.toml`.
