# Data Model: Batch Chapter URL Processing

## BatchInputRequest

- **Purpose**: Represents one execution of `extract` in file mode.
- **Fields**:
- `target_path`: Local path to the text file containing URLs.
- `save_enabled`: Whether successful chapter results should be written to
  `contents/`.
- `output_format`: Requested output mode for the run.
- **Validation Rules**:
- The path must exist, be readable, and reference a plain text input source for
  this feature.
- File mode must be explicit so path-based input is not confused with URL mode.

## BatchEntry

- **Purpose**: Represents one line from the batch input file.
- **Fields**:
- `line_number`: Original 1-based position in the file.
- `raw_value`: Original line content before trimming.
- `normalized_value`: Trimmed line content used for processing.
- `entry_state`: `skipped`, `queued`, `processed`, or `failed_validation`.
- **Validation Rules**:
- Blank normalized values are skipped.
- Duplicate normalized values are allowed and remain distinct by line number.

## BatchEntryResult

- **Purpose**: Captures the outcome of one processed batch entry.
- **Fields**:
- `line_number`: Source line number.
- `source_value`: Normalized URL string.
- `status`: `success`, `partial`, `failed`, or `skipped`.
- `skip_reason`: Optional explanation for skipped entries such as blank line.
- `chapter_result`: The per-URL extraction result when processing occurs.
- **Relationships**:
- References exactly one `ChapterResult` when the line is processed as a URL.
- Belongs to one `BatchResult`.

## ChapterResult

- **Purpose**: Existing per-chapter extraction and save result reused by both
  single and batch modes.
- **Relevant Existing Fields**:
- `source_url`
- `source_domain`
- `manga_title`
- `chapter_label`
- `status`
- `messages`
- `image_entries`
- `failure_reason`
- `save_result`
- **Usage Notes**:
- No separate extraction path is introduced for batch mode.
- Chapter-level failures remain visible inside the enclosing batch output.

## BatchSummary

- **Purpose**: Provides final counters for the user after the batch completes.
- **Fields**:
- `total_lines`: All lines read from the file.
- `processed_entries`: Non-blank lines attempted as URLs.
- `successful_entries`: Entries whose `ChapterResult` finished successfully.
- `failed_entries`: Entries that failed validation or extraction.
- `skipped_entries`: Blank or intentionally skipped lines.
- **Validation Rules**:
- Counts must reconcile with the number of `BatchEntryResult` items.

## BatchResult

- **Purpose**: Top-level aggregate returned by file mode execution.
- **Fields**:
- `target_path`
- `entries`: Ordered list of `BatchEntryResult`.
- `summary`: `BatchSummary`
- `messages`: Batch-level notes such as unreadable file or completion summary.
- **Relationships**:
- Contains zero or more `BatchEntryResult` items in file order.
- Owns one `BatchSummary`.

## State Transitions

- `BatchEntry.entry_state`: `queued` -> `processed`
- `BatchEntry.entry_state`: `queued` -> `failed_validation`
- `BatchEntry.entry_state`: `queued` -> `skipped`
- `BatchEntryResult.status`: `skipped` for blank lines, otherwise derived from
  the enclosed `ChapterResult`

## Notes

- The design intentionally keeps batch entities thin so the existing
  `ChapterResult` contract remains the core extraction unit.
- No persistence layer or resumable state is part of this feature.
