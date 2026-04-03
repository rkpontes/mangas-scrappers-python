# Implementation Plan: Batch Chapter URL Processing

**Branch**: `002-batch-url-extract` | **Date**: 2026-04-03 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-batch-url-extract/spec.md`

## Summary

Extend the existing `extract` CLI flow so the primary argument can represent
either a single chapter URL or a local text file when `--file` is provided.
The implementation stays inside the current CLI and scraper/service modules,
processes file entries sequentially, preserves per-chapter extraction and save
behavior, and adds a batch-oriented result summary without introducing new
infrastructure or dependencies.

## Technical Context

**Language/Version**: Python 3.12  
**Primary Dependencies**: `httpx`, `selectolax`, `typer`, `rich`  
**Storage**: Local filesystem under `contents/` and local text input files  
**Testing**: Manual validation for v1 plus `python3 -m py_compile $(find src -name '*.py' | sort)`  
**Target Platform**: Local CLI execution on developer machines  
**Project Type**: CLI application  
**Performance Goals**: Start one batch run for at least 10 chapter URLs from a
single file and produce a visible per-entry result for every line in one
execution  
**Constraints**: Reuse the existing `extract` command, support explicit file
mode with `--file`, continue after per-entry failures, preserve current save
layout, and avoid new dependencies or background processing  
**Scale/Scope**: Single operator, local text files, typical batches of 10-50
URLs, sequential processing only for v1

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- `PASS`: Scope remains limited to one useful feature slice by extending the
  current `extract` command rather than adding a separate subsystem.
- `PASS`: Structure stays within the existing CLI, scraper, and service modules
  with only small supporting models/helpers added if needed.
- `PASS`: Manual validation is explicit in the spec and will be restated in
  quickstart.
- `PASS`: No new dependencies are needed; the current stack already covers file
  reading, CLI parsing, rendering, and HTTP extraction.
- `PASS`: Error handling remains explicit through per-entry outcomes, final
  summary counts, and existing failure messages.

## Project Structure

### Documentation (this feature)

```text
specs/002-batch-url-extract/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── extract-batch-file.md
└── tasks.md
```

### Source Code (repository root)

```text
src/
├── cli/
│   └── main.py
├── scrapers/
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

**Structure Decision**: Keep the single-project CLI layout. The feature will be
implemented by extending [main.py](/Users/raphaelpontes/Documents/Projetos/Scrappers/mangas-scrappers/src/cli/main.py)
for command parsing, adding batch-oriented domain models in
[models.py](/Users/raphaelpontes/Documents/Projetos/Scrappers/mangas-scrappers/src/scrapers/models.py)
if needed, reusing [extractor.py](/Users/raphaelpontes/Documents/Projetos/Scrappers/mangas-scrappers/src/scrapers/extractor.py)
for per-URL extraction, and updating
[result_formatter.py](/Users/raphaelpontes/Documents/Projetos/Scrappers/mangas-scrappers/src/services/result_formatter.py)
to render batch summaries without adding new architectural layers.

## Phase 0: Research

### Decisions

- Use the existing `extract` command for both single and batch modes, with
  `--file` explicitly switching the primary argument from URL semantics to file
  path semantics.
- Process batch entries sequentially in file order for v1.
- Represent batch output as an aggregate result that contains per-entry chapter
  outcomes plus summary totals for succeeded, failed, and skipped entries.
- Reuse the current chapter extraction and image save flow for each URL rather
  than introducing a second extraction path.

### Rationale

- Reusing the same command preserves user familiarity and avoids multiplying CLI
  surface area.
- Sequential processing keeps control flow simple, predictable, and easier to
  debug when one source fails.
- An aggregate batch result is the smallest addition that supports both human
  and JSON output cleanly.
- Reusing current extraction and save behavior minimizes regression risk and
  stays aligned with the constitution's small-scope and simple-flow principles.

### Alternatives Considered

- Add a new `extract-file` command: rejected because it duplicates the current
  command surface and increases CLI complexity.
- Auto-detect file path versus URL without `--file`: rejected because explicit
  mode selection reduces ambiguity and validation mistakes.
- Process URLs concurrently: rejected for v1 because it adds coordination,
  ordering, and error-reporting complexity without being required by the spec.

## Phase 1: Design & Contracts

### Data Model Design

- Add a batch-level request concept for file mode input and save/output
  preferences.
- Add a batch entry concept that preserves source line position, normalized
  value, and whether the line was skipped or processed.
- Add a batch result concept that groups per-entry chapter outcomes and final
  counters for processed, succeeded, failed, and skipped lines.
- Keep `ChapterResult` as the per-URL extraction contract so single and batch
  modes share the same extraction and save behavior.

### Interface Contracts

- Define a CLI contract for `extract <target> [--file] [--save] [--output-format
  ...]`.
- Specify validation differences between URL mode and file mode.
- Define batch exit-code behavior so failures remain actionable without hiding
  partial success.
- Define the visible summary contract for both human-readable and JSON output.

### Manual Validation Strategy

- Validate single-command batch execution with a file containing multiple valid
  chapter URLs.
- Validate mixed batches containing blank lines, invalid URLs, unsupported
  sources, and duplicate URLs.
- Validate save behavior through `--file --save`, confirming successful entries
  write under the existing `contents/` organization while failures remain
  visible.
- Validate syntax correctness with `py_compile` after code changes.

## Phase 2: Task Planning Approach

- Update CLI argument parsing and target validation in `src/cli/main.py`.
- Introduce the minimum batch domain models and helpers required in
  `src/scrapers/models.py` and potentially a small file-reading helper near the
  CLI if it improves clarity.
- Reuse `ChapterExtractor` and `ImageDownloader` per URL, composing them into a
  batch loop without changing adapter behavior.
- Extend result rendering in `src/services/result_formatter.py` for per-entry
  output and summary totals.
- Keep implementation increments reviewable: parsing, batch execution, output,
  and manual verification artifacts.

## Post-Design Constitution Check

- `PASS`: Design remains a small extension of the current CLI flow.
- `PASS`: No extra service layer, worker, or dependency was introduced.
- `PASS`: Manual validation remains the primary quality gate for v1.
- `PASS`: Error reporting is explicit at file, line, chapter, and summary
  levels.
- `PASS`: The feature can be implemented by touching a small number of existing
  files plus the planning artifacts.

## Complexity Tracking

No constitution violations requiring justification.
