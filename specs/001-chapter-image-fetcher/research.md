# Research: Manga Chapter Image Extraction

## Decision: Build the first version as a local Python CLI

Rationale:
- The constitution prefers a small, single-purpose application.
- A CLI is the smallest useful interface for taking a URL and saving files.
- It avoids adding browser UI, local web servers, or deployment concerns.

Alternatives considered:
- Desktop GUI application: rejected as unnecessary scope for v1.
- Web application: rejected because it adds routing, hosting, and browser state.

## Decision: Support only publicly accessible chapter pages in v1

Rationale:
- This keeps the feature within the allowed-access constraints in the spec.
- It avoids session management, credential handling, and higher security risk.
- It produces clearer manual validation steps and fewer ambiguous failure modes.

Alternatives considered:
- User-supplied cookies: rejected for v1 because it complicates input handling
  and security posture.
- Built-in login flows: rejected because it materially expands scope.

## Decision: Use `httpx` for HTTP fetching

Rationale:
- It provides a straightforward synchronous client for a small CLI.
- Timeouts, headers, and redirects can be handled cleanly.
- The dependency is lightweight for the required feature set.

Alternatives considered:
- `requests`: acceptable, but `httpx` offers a cleaner path if async is ever
  needed later without changing core interfaces.
- Browser automation: rejected because most of the needed flow is plain HTTP.

## Decision: Use `selectolax` for HTML parsing

Rationale:
- It is fast and simple for extracting image URLs from HTML documents.
- The parser is lighter than a broader crawler framework.
- The code stays focused on extraction rules instead of crawler orchestration.

Alternatives considered:
- `BeautifulSoup`: viable, but heavier and slower for repeated DOM selection.
- `Scrapy`: useful for large crawling workflows, but too much framework for a
  single-URL extraction tool.

## Decision: Use a small adapter-based extraction design

Rationale:
- A generic adapter can try common extraction heuristics for any public site.
- A MangaDex-specific adapter can improve reliability for a recommended source.
- This keeps source-specific logic localized without overengineering the core.

Alternatives considered:
- Single generic parser only: rejected because recommended sources benefit from
  explicit handling.
- Dedicated adapter per site from the start: rejected as too much upfront work.

## Decision: Save files under `/contents/<manga title>/<chapter label>/`

Rationale:
- The required output structure is explicit in the clarified specification.
- A deterministic path makes manual validation and repeated use predictable.
- Keeping image extensions preserves the original file type without guessing.

Alternatives considered:
- Flat output directory: rejected because chapters and series would collide.
- Archive-only output: rejected because the spec requires direct file saving.

## Decision: Use `typer` plus `rich` for CLI interaction

Rationale:
- `typer` keeps argument parsing small and readable.
- `rich` improves success/error readability during manual validation.
- Both dependencies serve the primary user interaction directly.

Alternatives considered:
- `argparse` only: viable, but more verbose for a small command surface.
- No formatted output dependency: rejected because error readability matters in
  a manual-validation-first workflow.
