# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- User-configurable connection timeout.

### Changed

- Replaced `requests` dependency with the standard library's `urllib`.
- Converted `Article`, `PDF`, and `Summary` to dataclasses.
- Simplified exception types.

## [1.0.1] - 2026-03-20

### Added

- Markdown output for Article and PDF APIs.

[Unreleased]: https://github.com/Instapaper/instaparser-python/compare/v1.0.1...HEAD
[1.0.1]: https://github.com/Instapaper/instaparser-python/compare/v1.0.0...v1.0.1
