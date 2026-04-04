# Data Model: Title-Based Chapter Extraction

## ChapterRequest

- **Purpose**: Represents one execution of `extract-chapter` for a direct
  chapter URL.
- **Fields**:
- `source_url`: Chapter URL to extract.
- `save_enabled`: Whether successful chapter results should be written to
  `contents/`.
- `save_root`: Root output path for saved images.
- `compatibility_hint`: Optional source hint carried from the existing flow.
- **Validation Rules**:
- The URL must be an absolute HTTP/HTTPS chapter URL.

## BatchInputRequest

- **Purpose**: Represents one execution of `extract-chapter` in file mode.
- **Fields**:
- `target_path`: Local path to the text file containing chapter URLs.
- `save_enabled`: Whether successful chapter results should be written to
  `contents/`.
- `output_format`: Requested output mode for the run.
- **Validation Rules**:
- File mode must be explicit.
- The path must exist, be readable, and resolve to a plain text input source.

## TitleInputRequest

- **Purpose**: Represents one execution of `extract-title`, either by direct
  title URL or by local text file.
- **Fields**:
- `target_value`: Raw CLI target value.
- `file_mode`: Whether `target_value` should be treated as a local file path.
- `save_enabled`: Whether successful discovered chapters should be written to
  `contents/`.
- `output_format`: Requested output mode for the run.
- **Validation Rules**:
- Direct mode requires a valid MangaDex title URL.
- File mode requires a readable local text file.

## TitleInputEntry

- **Purpose**: Represents one line from a title input file.
- **Fields**:
- `line_number`: Original 1-based file position.
- `raw_value`: Original line content before trimming.
- `normalized_value`: Trimmed value used for validation and processing.
- `entry_state`: `skipped`, `queued`, `processed`, or `failed_validation`.
- **Validation Rules**:
- Blank normalized values are skipped.
- Duplicate normalized values are allowed and remain distinct by line number.

## TitleDiscovery

- **Purpose**: Represents the chapter-discovery result for one title request.
- **Fields**:
- `title_url`: Source MangaDex title URL.
- `title_label`: Human-readable title label for output.
- `chapter_urls`: Ordered discovered chapter URLs after de-duplication.
- `duplicate_chapter_urls`: Any repeated chapter URLs removed within the same
  title listing.
- `messages`: Discovery notes shown to the user.
- **Validation Rules**:
- Chapter URLs must remain unique within one title discovery result.
- An empty chapter list is allowed and must be reported explicitly.

## TitleChapterResult

- **Purpose**: Captures the outcome of one discovered chapter inside a title
  run.
- **Fields**:
- `chapter_index`: 1-based chapter position within the discovered title list.
- `source_value`: Chapter URL requested from discovery.
- `status`: `success`, `partial`, `failed`, or `skipped`.
- `chapter_result`: The reused per-chapter extraction result.
- **Relationships**:
- References exactly one `ChapterResult` when the chapter is attempted.
- Belongs to one `TitleResult`.

## TitleResult

- **Purpose**: Captures the complete outcome for one title request.
- **Fields**:
- `source_value`: Direct title URL or normalized title input value from file
  mode.
- `source_line`: Optional source line number when the title came from a file.
- `status`: `success`, `partial`, `failed`, or `skipped`.
- `discovery`: `TitleDiscovery` when title validation and discovery succeeded.
- `chapter_results`: Ordered list of `TitleChapterResult`.
- `messages`: Title-level notes such as validation, no-chapter, or completion
  messages.
- **Validation Rules**:
- Invalid titles may fail before discovery.
- A title with zero discovered chapters remains a valid processed title result
  with no `chapter_results`.

## TitleRunSummary

- **Purpose**: Provides final counters after `extract-title` completes.
- **Fields**:
- `total_lines`: All lines read from a title input file, `0` in direct mode.
- `processed_titles`: Titles attempted after blank-line filtering.
- `successful_titles`: Titles whose discovered chapters all succeeded or were
  otherwise reported as successful according to the chosen result rule.
- `failed_titles`: Titles that failed validation, discovery, or contained
  failed chapter work.
- `skipped_titles`: Blank or intentionally skipped title entries.
- `discovered_chapters`: Total unique chapter URLs discovered across processed
  titles.
- `successful_chapters`: Chapters whose `ChapterResult` finished successfully.
- `failed_chapters`: Chapters that failed extraction or saving.
- `skipped_chapters`: Chapters skipped intentionally, if such a state is later
  needed.
- **Validation Rules**:
- Summary counts must reconcile with the ordered `TitleResult` entries and
  their chapter results.

## TitleRunResult

- **Purpose**: Top-level aggregate returned by `extract-title` in direct or
  file mode.
- **Fields**:
- `target_value`: Direct title URL or source file path.
- `file_mode`: Whether the run was driven by a local file.
- `entries`: Ordered list of `TitleResult`.
- `summary`: `TitleRunSummary`
- `messages`: Run-level notes such as completion summary.
- **Relationships**:
- Contains one `TitleResult` in direct mode or zero-or-more ordered entries in
  file mode.
- Owns one `TitleRunSummary`.

## ChapterResult

- **Purpose**: Existing per-chapter extraction and save result reused by both
  `extract-chapter` and `extract-title`.
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
- No separate chapter image extraction contract is introduced for title mode.
- Title orchestration wraps `ChapterResult` rather than replacing it.

## State Transitions

- `TitleInputEntry.entry_state`: `queued` -> `processed`
- `TitleInputEntry.entry_state`: `queued` -> `failed_validation`
- `TitleInputEntry.entry_state`: `queued` -> `skipped`
- `TitleResult.status`: `failed` when title validation or discovery fails
- `TitleResult.status`: `success` or `partial` based on aggregated chapter
  outcomes
- `TitleChapterResult.status`: derived from the enclosed `ChapterResult`

## Notes

- The design intentionally keeps title entities thin so the existing
  `ChapterResult` remains the central extraction unit.
- No persistence layer, resumable state, or background job tracking is part of
  this feature.
