# Implementation Plan: Title-Based Chapter Extraction

**Branch**: `003-extract-title-chapters` | **Date**: 2026-04-03 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-extract-title-chapters/spec.md`

## Summary

Split the current CLI surface into `extract-chapter` and `extract-title`,
while keeping the existing chapter extraction flow as the core unit of work.
`extract-title` will accept either one MangaDex title URL or a local text file
when `--file` is provided, discover the chapter URLs for each title, process
them sequentially through the existing chapter extraction path, and render
per-chapter plus aggregate title summaries without adding new infrastructure or
dependencies.

## Technical Context

**Language/Version**: Python 3.12  
**Primary Dependencies**: `httpx`, `selectolax`, `typer`, `rich`  
**Storage**: Local filesystem under `contents/` and local text input files  
**Testing**: Manual validation for v1 plus `python3 -m py_compile $(find src -name '*.py' | sort)`  
**Target Platform**: Local CLI execution on developer machines  
**Project Type**: CLI application  
**Performance Goals**: Start one title extraction run from either a single
MangaDex title URL or a local file of title URLs and produce a visible outcome
for every processed title and discovered chapter in one execution  
**Constraints**: Keep the flow synchronous for v1, preserve current save
layout, require explicit `--file` mode for local file input, scope title
support to MangaDex URLs, and avoid new dependencies or background processing  
**Scale/Scope**: Single operator, local runs, typical title files containing
1-20 title URLs, titles ranging from a few chapters to a few hundred chapters,
sequential processing only for v1

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- `PASS`: Scope stays limited to a CLI rename plus one new title-oriented
  execution path; no generic source-discovery framework is introduced.
- `PASS`: Structure remains inside the current CLI, scraper, model, and
  formatter modules with only small helper/model additions if needed.
- `PASS`: Manual validation is explicit in the spec and will be restated in
  quickstart for URL mode, file mode, and save mode.
- `PASS`: No new dependencies are required; current libraries already cover CLI
  parsing, HTTP access, JSON parsing, rendering, and filesystem output.
- `PASS`: Error handling remains explicit through title validation, file access
  errors, per-title outcomes, per-chapter outcomes, and final summaries.

## Project Structure

### Documentation (this feature)

```text
specs/003-extract-title-chapters/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── cli-commands.md
└── tasks.md
```

### Source Code (repository root)

```text
src/
├── cli/
│   └── main.py
├── scrapers/
│   ├── adapters/
│   │   └── mangadex.py
│   ├── extractor.py
│   └── models.py
├── services/
│   ├── image_downloader.py
│   ├── path_builder.py
│   └── result_formatter.py
└── lib/
    └── text.py

specs/
contents/
```

**Structure Decision**: Keep the existing single-project CLI layout. Implement
command renaming and title/file orchestration in
[main.py](/Users/raphaelpontes/Documents/Projetos/Scrappers/mangas-scrappers/src/cli/main.py),
extend [models.py](/Users/raphaelpontes/Documents/Projetos/Scrappers/mangas-scrappers/src/scrapers/models.py)
with the smallest set of title-oriented request/result types, add MangaDex
title discovery in
[mangadex.py](/Users/raphaelpontes/Documents/Projetos/Scrappers/mangas-scrappers/src/scrapers/adapters/mangadex.py),
reuse [extractor.py](/Users/raphaelpontes/Documents/Projetos/Scrappers/mangas-scrappers/src/scrapers/extractor.py)
for per-chapter work, extend
[result_formatter.py](/Users/raphaelpontes/Documents/Projetos/Scrappers/mangas-scrappers/src/services/result_formatter.py)
for title-oriented output, and keep small parsing helpers in
[text.py](/Users/raphaelpontes/Documents/Projetos/Scrappers/mangas-scrappers/src/lib/text.py)
if title URL parsing needs to be shared.

## Phase 0: Research

### Decisions

- Rename the existing chapter command to `extract-chapter` and reserve
  `extract-title` for title-driven discovery and orchestration.
- Keep explicit `--file` semantics for both commands instead of auto-detecting
  URLs versus file paths.
- Use MangaDex public API data already aligned with the current adapter flow to
  discover chapter URLs for a title, rather than scraping the title HTML page.
- Process titles sequentially, and within each title process chapters
  sequentially in discovered order for v1.
- Reuse the current per-chapter extraction and save flow as the execution unit,
  wrapping it with thin title-level request, result, and summary models.
- Treat duplicate title URLs in input files as intentional repeated requests,
  while de-duplicating repeated chapter URLs returned within one title listing.

### Rationale

- Splitting command names makes the CLI intent explicit without creating more
  than the two user-facing entrypoints now required by the spec.
- Explicit `--file` mode preserves the current mental model and avoids
  ambiguous validation rules.
- The existing MangaDex adapter already relies on the public API for chapter
  metadata and page discovery, so extending that path for title discovery keeps
  the integration coherent and simpler than mixing API and HTML scraping.
- Sequential processing keeps output deterministic and avoids introducing
  concurrency, progress coordination, or save collisions across multiple
  chapters.
- Thin title-level wrappers preserve the current `ChapterResult` contract and
  minimize regression risk in extraction and saving code.
- Separating duplicate-title and duplicate-chapter behavior matches the spec:
  repeated user inputs stay intentional, but redundant source listings should
  not multiply work inside a single title run.

### Alternatives Considered

- Keep one generic `extract` command with additional mode flags: rejected
  because the spec now requires clearer command separation between chapter and
  title flows.
- Auto-detect local files without `--file`: rejected because explicit mode is
  easier to validate and debug.
- Scrape MangaDex title page HTML for chapter links: rejected because the
  project already uses the public API and HTML scraping would add avoidable
  brittleness.
- Process titles or chapters concurrently: rejected for v1 because it adds
  coordination complexity without being required for the initial feature slice.

## Phase 1: Design & Contracts

### Data Model Design

- Keep `ChapterResult` as the per-chapter extraction contract shared by
  `extract-chapter` and `extract-title`.
- Add a title request concept that supports either direct title URL mode or
  file mode input and keeps save/output preferences for the run.
- Add title-input entry models for local file mode so per-line title validation
  and skip behavior stays explicit.
- Add title discovery models that preserve title identity, discovered chapter
  URLs, de-duplication decisions, and per-title execution status.
- Add title-run summary models that count processed titles and discovered,
  attempted, successful, failed, and skipped chapters.
- Reuse existing batch concepts where that reduces duplication, but prefer
  title-specific naming when a model now represents title-level behavior rather
  than generic chapter batch behavior.

### Interface Contracts

- Define the renamed chapter command contract for
  `extract-chapter <target> [--file] [--save] [--output-format ...]`.
- Define the title command contract for
  `extract-title <target> [--file] [--save] [--output-format ...]`.
- Specify validation differences for direct URL mode versus explicit file mode.
- Define human-readable and JSON output expectations for per-title and
  per-chapter results.
- Define exit-code behavior so title-level or chapter-level failures remain
  actionable without hiding partial success.

### Manual Validation Strategy

- Validate renamed chapter execution for a single chapter URL and for a local
  file of chapter URLs.
- Validate `extract-title` with one valid MangaDex title URL containing
  multiple chapters.
- Validate `extract-title --file` with a local text file containing multiple
  title URLs, blank lines, duplicates, and an invalid entry.
- Validate save behavior through both `extract-chapter --save` and
  `extract-title --save`, confirming that successful chapters continue to use
  the existing `contents/` structure.
- Validate syntax correctness with `py_compile` after code changes.

## Phase 2: Task Planning Approach

- Update CLI command registration, shared validation helpers, and exit-code
  handling in `src/cli/main.py`.
- Add the minimum title-oriented request/result models needed in
  `src/scrapers/models.py`, keeping existing chapter result shapes intact where
  possible.
- Extend the MangaDex adapter with title discovery support and small shared URL
  parsing helpers in `src/lib/text.py` if needed.
- Compose title runs from the existing chapter extraction and save flow rather
  than adding a second extractor stack.
- Extend `src/services/result_formatter.py` so human and JSON output cover
  chapter mode, title mode, and file-driven summaries consistently.
- Keep implementation increments reviewable: CLI surface rename, title
  discovery, title orchestration, rendering, and manual validation artifacts.

## Post-Design Constitution Check

- `PASS`: The design stays within one small CLI application and avoids generic
  abstraction layers.
- `PASS`: The implementation can be delivered by changing a small set of
  existing files plus the planning artifacts.
- `PASS`: Manual validation remains the delivery gate for v1 and is explicit
  for renamed chapter flow and new title flow.
- `PASS`: No new dependency, worker, persistence layer, or background process
  was introduced.
- `PASS`: Error reporting stays explicit at file, title, chapter, save, and
  summary levels.

## Complexity Tracking

No constitution violations requiring justification.
