# Research: Batch Chapter URL Processing

## Decision 1: Keep a single `extract` command with explicit file mode

**Decision**: Batch processing will reuse the existing `extract` command and
accept a local file path as the primary target only when `--file` is present.

**Rationale**: This keeps the CLI surface small, preserves the user's mental
model, and avoids duplicating extraction logic behind a second command.

**Alternatives considered**:

- Add a dedicated `extract-file` command.
- Auto-detect whether the primary argument is a URL or a local file path.

## Decision 2: Process batch entries sequentially

**Decision**: URLs from the input file will be processed one by one in source
line order.

**Rationale**: Sequential handling preserves deterministic output order, fits
the current synchronous extraction flow, and keeps failures easier to debug.

**Alternatives considered**:

- Concurrent chapter extraction with shared HTTP or save coordination.
- Chunked or resumable batch execution.

## Decision 3: Reuse `ChapterResult` as the per-entry result unit

**Decision**: Each processed URL in batch mode will still produce the same
chapter-level result shape already used by single-URL extraction, wrapped by a
small batch aggregate result.

**Rationale**: This minimizes branching in extraction and save code, allowing
existing rendering and failure semantics to be extended rather than replaced.

**Alternatives considered**:

- Create a separate batch-only per-entry result format unrelated to
  `ChapterResult`.
- Flatten all pages across all chapters into one monolithic result object.

## Decision 4: Skip blank lines and continue after per-entry failures

**Decision**: Blank lines are skipped, invalid entries are reported
individually, and later URLs continue processing even when earlier ones fail.

**Rationale**: This matches the feature spec, prevents one bad line from
discarding the rest of the batch, and gives the user a clear retry target list.

**Alternatives considered**:

- Stop on first invalid or failed entry.
- Pre-validate the entire file and abort the run if any line is invalid.

## Decision 5: Keep v1 dependency-free and filesystem-local

**Decision**: The feature will use only the current standard library and
existing project dependencies, reading URLs from a local text file and saving
through the current `contents/` flow.

**Rationale**: The current stack already supports CLI parsing, HTTP requests,
rendering, and filesystem output. Additional libraries would add weight without
reducing present complexity.

**Alternatives considered**:

- Introduce a CSV or queue-processing dependency.
- Add persistent state for resumable batches.
