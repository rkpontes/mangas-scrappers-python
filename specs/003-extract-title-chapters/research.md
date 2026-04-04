# Research: Title-Based Chapter Extraction

## Decision 1: Split the CLI into `extract-chapter` and `extract-title`

**Decision**: The current chapter extraction command will be renamed to
`extract-chapter`, and title-driven extraction will use a separate
`extract-title` command.

**Rationale**: The feature now has two distinct user intents. Separate command
names keep the CLI explicit while still preserving a very small surface area.

**Alternatives considered**:

- Keep one overloaded `extract` command with extra mode flags.
- Add a third helper command dedicated only to file input.

## Decision 2: Keep explicit `--file` mode for both commands

**Decision**: Both `extract-chapter` and `extract-title` will accept a local
text file only when `--file` is provided.

**Rationale**: Explicit file mode avoids ambiguity between URL validation and
file-path validation, keeps error messages straightforward, and matches the
existing batch-input pattern already established in the project.

**Alternatives considered**:

- Auto-detect whether the target is a URL or a local file path.
- Use different flag names for title files and chapter files.

## Decision 3: Discover title chapters through the MangaDex public API path

**Decision**: Title chapter discovery for `extract-title` will extend the
current MangaDex integration path that already uses public API responses for
chapter extraction.

**Rationale**: Reusing the same integration style keeps the adapter behavior
consistent, reduces brittleness versus parsing title HTML, and avoids
introducing a second source-discovery mechanism for the same domain.

**Alternatives considered**:

- Scrape the MangaDex title page HTML for chapter links.
- Introduce a separate title-discovery service unrelated to the existing
  adapter.

## Decision 4: Process titles and chapters sequentially

**Decision**: Title input files will be processed one title at a time, and each
title's discovered chapters will be extracted one by one in discovered order.

**Rationale**: Sequential handling preserves deterministic output, keeps
failures easier to diagnose, and avoids coordination complexity in saving and
reporting.

**Alternatives considered**:

- Run titles concurrently while keeping chapters sequential.
- Run both titles and chapters concurrently.
- Add resumable or queued background processing.

## Decision 5: Reuse chapter extraction as the execution unit

**Decision**: `extract-title` will orchestrate title discovery and then invoke
the same per-chapter extraction and save flow already used by
`extract-chapter`.

**Rationale**: This minimizes branching in extraction logic, preserves current
save behavior, and limits the new code to orchestration plus title-oriented
reporting.

**Alternatives considered**:

- Build a separate title-only extraction pipeline with its own chapter page
  handling.
- Flatten title output into a single custom structure that bypasses
  `ChapterResult`.

## Decision 6: Preserve duplicate-title inputs but deduplicate duplicate chapter listings

**Decision**: Repeated title URLs in a file will be processed once per
occurrence, while duplicate chapter URLs returned inside one title listing will
be processed only once for that title.

**Rationale**: Duplicate title lines reflect explicit user input and should
stay intentional, but duplicate chapter listings from the source are noise that
would waste work and produce confusing repeated results.

**Alternatives considered**:

- Deduplicate title file entries automatically.
- Process duplicate chapter listings exactly as returned by the source.

## Decision 7: Keep the feature dependency-free and filesystem-local

**Decision**: The feature will rely only on the current project stack and local
filesystem inputs/outputs.

**Rationale**: Existing dependencies already cover CLI parsing, HTTP access,
JSON handling, rendering, and saving. Additional libraries or services would
increase complexity without solving a current gap.

**Alternatives considered**:

- Add a job-state or queue dependency for long-running title batches.
- Add a CSV or manifest parser beyond plain local text files.
