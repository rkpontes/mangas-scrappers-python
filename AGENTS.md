# mangas-scrappers Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-04-03

## Active Technologies
- Local filesystem under `contents/` and local text input files (002-batch-url-extract)

- Python 3.12 + `httpx`, `selectolax`, `typer`, `rich` (001-chapter-image-fetcher)

## Project Structure

```text
src/
specs/
contents/
```

## Commands

- `python3 -m venv .venv`
- `source .venv/bin/activate`
- `pip install -e .`
- `python3 -m src.cli.main --help`
- `python3 -m src.cli.main extract "<chapter-url>"`
- `python3 -m src.cli.main extract "<chapter-url>" --save`
- `python3 -m src.cli.main extract "<file-path>" --file`
- `python3 -m src.cli.main extract "<file-path>" --file --save`
- `python3 -m py_compile $(find src -name '*.py' | sort)`

## Code Style

Python 3.12: Follow standard conventions

## Recent Changes
- 002-batch-url-extract: Added Python 3.12 + `httpx`, `selectolax`, `typer`, `rich`

- 001-chapter-image-fetcher: Added Python 3.12 + `httpx`, `selectolax`, `typer`, `rich`

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
