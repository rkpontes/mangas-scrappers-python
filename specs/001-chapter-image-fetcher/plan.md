# Implementation Plan: Manga Chapter Image Extraction

**Branch**: `001-chapter-image-fetcher` | **Date**: 2026-04-03 | **Spec**: [/Users/raphaelpontes/Documents/Projetos/Scrappers/mangas-scrappers/specs/001-chapter-image-fetcher/spec.md](/Users/raphaelpontes/Documents/Projetos/Scrappers/mangas-scrappers/specs/001-chapter-image-fetcher/spec.md)
**Input**: Feature specification from `/specs/001-chapter-image-fetcher/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Build a small CLI application that accepts a manga chapter URL, extracts the
ordered list of chapter images from publicly accessible pages the user is
allowed to access, and optionally saves those images under
`/contents/<manga title>/<chapter label>/<image index>.<image extension>`.
The implementation will use a lightweight adapter-based scraping flow so the
core extraction pipeline stays simple while recommended sources such as
MangaDex can have clearer compatibility handling.

## Technical Context

**Language/Version**: Python 3.12  
**Primary Dependencies**: `httpx`, `selectolax`, `typer`, `rich`  
**Storage**: Local filesystem under `/contents/`; no database  
**Testing**: Manual validation only for v1, documented in `quickstart.md`  
**Target Platform**: Local desktop or terminal environment on macOS/Linux  
**Project Type**: CLI application  
**Performance Goals**: Start extraction in under 30 seconds and save a typical
chapter in a single command flow  
**Constraints**: Publicly accessible pages only, no login automation, no access
control bypassing, keep dependency count low, preserve original image extension  
**Scale/Scope**: Single-user local tool, a small list of recommended sites, and
best-effort extraction for other public chapter URLs

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Scope remains limited to the smallest useful feature slice.
- Structure uses the fewest modules/layers needed for the current feature.
- Manual validation steps are defined for each user story.
- New dependencies are justified by reducing present complexity.
- Error handling and logs are explicit enough for manual debugging.

Gate status: PASS
- The feature remains a single CLI application with local filesystem output.
- The design uses a narrow adapter seam only for source-specific extraction.
- Manual validation is documented in `quickstart.md`.
- Dependencies are limited to HTTP fetching, HTML parsing, CLI argument
  handling, and readable terminal output.
- Failure modes remain explicit and user-visible.

## Project Structure

### Documentation (this feature)

```text
specs/001-chapter-image-fetcher/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
src/
├── cli/
│   └── main.py
├── scrapers/
│   ├── adapters/
│   │   ├── base.py
│   │   ├── generic.py
│   │   └── mangadex.py
│   ├── extractor.py
│   └── models.py
├── services/
│   ├── image_downloader.py
│   ├── path_builder.py
│   └── result_formatter.py
└── lib/
    ├── http_client.py
    ├── html_parser.py
    └── text.py

contents/
└── <manga title>/<chapter label>/<image index>.<image extension>

specs/001-chapter-image-fetcher/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
└── contracts/
    └── cli-contract.md
```

**Structure Decision**: Use a single-project CLI structure. `src/scrapers/`
owns extraction and source adaptation, `src/services/` owns saving and output
formatting, and `src/lib/` contains small infrastructure helpers only. This is
the smallest structure that still isolates source-specific parsing from generic
save and reporting behavior.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Additional source adapter files | Different sites expose chapter pages differently | A single parser would become harder to read and maintain |
| `rich` dependency for terminal output | Clearer user-facing result and error display | Plain `print` output is harder to scan during manual validation |
