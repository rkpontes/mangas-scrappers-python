# Feature Specification: Batch Chapter URL Processing

**Feature Branch**: `002-batch-url-extract`  
**Created**: 2026-04-03  
**Status**: Draft  
**Input**: User description: "Vamos fazer um ajuste na aplicação, onde teremos um arquivo de texto contendo as urls (1 por linha) e o app fazer o scrapping de todas as urls"

## Clarifications

### Session 2026-04-03

- Q: Como o usuário aciona o processamento em lote no comando `extract-chapter`? → A: O usuário informa um caminho de arquivo no argumento principal e ativa o modo de arquivo com `--file`, por exemplo `python3 -m src.cli.main extract-chapter <file-path> --file --save`.

## User Scenarios & Validation *(mandatory)*

### User Story 1 - Process a List of Chapter URLs (Priority: P1)

As a user, I want to provide a text file with one chapter URL per line so I can
run extraction for multiple chapters in one execution instead of repeating the
same command manually.

**Why this priority**: This is the requested behavior change and delivers the
main user value by removing repetitive one-by-one execution.

**Independent Validation**: Run the application with a text file that contains
multiple valid chapter URLs on separate lines, confirm that the system attempts
all listed chapters in a single run, and verify that each chapter produces its
own visible result.

**Acceptance Scenarios**:

1. **Given** a text file with multiple valid chapter URLs separated by line
   breaks, **When** the user starts batch processing, **Then** the system reads
   each non-empty line as a distinct chapter request and attempts extraction for
   all listed chapters in the same run.
2. **Given** a text file that contains leading or trailing spaces around valid
   URLs, **When** the file is processed, **Then** the system ignores the extra
   whitespace and still treats each line as the intended chapter URL.

---

### User Story 2 - Review Per-URL Outcomes (Priority: P2)

As a user, I want to see which chapter URLs succeeded or failed during batch
processing so I can retry only the failed items instead of rerunning the entire
list blindly.

**Why this priority**: Batch processing is only practical if the user can
understand the result of each URL independently.

**Independent Validation**: Run the application with a text file containing a
mix of valid, invalid, and unsupported chapter URLs, then confirm that the
output clearly identifies the outcome for each line without hiding failures.

**Acceptance Scenarios**:

1. **Given** a batch file that mixes successful and unsuccessful chapter URLs,
   **When** processing completes, **Then** the system reports a distinct result
   for each URL, including clear failure reasons where extraction did not
   succeed.
2. **Given** one URL in the file fails validation or extraction, **When** the
   batch continues, **Then** the system still attempts the remaining URLs
   instead of stopping the entire run after the first error.

---

### User Story 3 - Save Batch Results Predictably (Priority: P3)

As a user, I want successful chapters from a batch file to be saved using the
same predictable organization as single-chapter extraction so I can manage the
downloaded content without learning a separate workflow.

**Why this priority**: Reusing the established save behavior keeps the feature
consistent and prevents the batch flow from producing confusing output.

**Independent Validation**: Run the application with a text file of valid URLs
and saving enabled, confirm that each successful chapter is written to its own
destination, and verify that failures do not remove or corrupt successful
saves.

**Acceptance Scenarios**:

1. **Given** batch processing with saving enabled and multiple successful
   chapters, **When** extraction completes, **Then** each successful chapter is
   stored using the same folder and file naming rules already used for
   individual chapters.
2. **Given** a batch where some chapters fail after others succeed, **When**
   the run finishes, **Then** the saved output for successful chapters remains
   available and the failed chapters are reported separately.

### Edge Cases

- What happens when the provided file path does not exist or cannot be read?
- How does the system handle blank lines in the file?
- What happens when the same chapter URL appears more than once in the same
  file?
- How does the system behave when every URL in the file fails validation or
  extraction?
- What happens when a batch mixes URLs that save successfully with URLs that
  fail due to unsupported or inaccessible sources?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST allow the user to provide a plain text file as
  batch input for chapter extraction.
- **FR-001a**: The system MUST support batch input through the existing
  `extract-chapter` entrypoint by accepting a file path as the primary extraction
  target when file mode is explicitly requested.
- **FR-002**: The system MUST treat each non-empty line in the file as one
  chapter URL request.
- **FR-003**: The system MUST ignore leading and trailing whitespace around each
  line before evaluating it as a URL.
- **FR-004**: The system MUST skip blank lines without treating them as
  extraction failures.
- **FR-005**: The system MUST attempt extraction for every valid line in the
  file during the same batch run.
- **FR-006**: The system MUST preserve the existing single-chapter extraction
  behavior for each URL processed from the file.
- **FR-007**: The system MUST report an individual outcome for each processed
  URL, including whether it succeeded or failed.
- **FR-008**: The system MUST continue processing remaining URLs after a
  validation or extraction failure on an earlier line.
- **FR-009**: The system MUST provide a clear summary of how many URLs
  succeeded, failed, or were skipped by the end of the batch run.
- **FR-010**: When saving is enabled, the system MUST save each successful
  chapter using the same destination and naming rules defined for single-URL
  extraction.
- **FR-011**: The system MUST keep successful saves intact even when other URLs
  in the same batch fail.
- **FR-012**: The system MUST show a clear error when the provided file cannot
  be found or read.
- **FR-013**: The system MUST allow duplicate URLs in the file and process each
  occurrence as a separate requested attempt.

### Key Entities *(include if feature involves data)*

- **Batch Input File**: A user-provided text file containing chapter URLs, with
  one intended request per non-empty line.
- **Batch Entry**: A single normalized line from the batch file, including its
  original position and requested chapter URL.
- **Batch Result**: The per-entry outcome describing success, failure, skip
  status, and any chapter-specific extraction details needed by the user.
- **Batch Summary**: The final totals for processed, successful, failed, and
  skipped entries shown after the batch run completes.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A user can start extraction for at least 10 chapter URLs from one
  text file in a single execution without manually repeating the command for
  each URL.
- **SC-002**: In manual validation with a mixed batch file, 100% of URLs in the
  file produce a visible per-entry outcome of success, failure, or skip by the
  end of the run.
- **SC-003**: In manual validation, a failure on one URL does not prevent later
  URLs in the same file from being attempted.
- **SC-004**: When saving is enabled for a batch of valid chapter URLs, 100% of
  successful chapters are stored using the same organization pattern already
  used for single-chapter saves.
- **SC-005**: A user can determine from the final summary, in under 30 seconds,
  how many URLs succeeded, failed, or were skipped in the batch.

## Manual Validation Plan *(mandatory for v1 without automated tests)*

- Create a sample text file with multiple valid chapter URLs, one per line, and
  run the batch flow through `python3 -m src.cli.main extract-chapter <file-path>
  --file`.
- Confirm that each listed URL produces its own visible extraction outcome in
  the same execution.
- Create a second sample file containing blank lines, repeated URLs, and at
  least one invalid or unsupported URL.
- Confirm that blank lines are skipped, repeated URLs are processed as separate
  attempts, and failures do not stop later lines from being processed.
- Run the batch flow with saving enabled through
  `python3 -m src.cli.main extract-chapter <file-path> --file --save` for a file
  containing multiple valid URLs and confirm that each successful chapter is
  written using the existing save organization.
- Run the batch flow with a missing or unreadable file path and confirm that the
  system returns a clear file access error.
- Confirm that the final output includes totals for successful, failed, and
  skipped entries.

## Assumptions

- The primary user is the same single operator already using the application
  for one-by-one chapter extraction and now wants a faster batch workflow.
- The existing single-URL extraction and optional save behavior remain valid and
  are reused per URL in batch mode, with batch input selected explicitly
  through file mode on `extract-chapter`.
- The batch input file is encoded as ordinary readable text and is prepared by
  the user outside the application.
- First version scope is limited to sequential processing of URLs from a local
  text file; advanced queue management, scheduling, and remote file sources are
  out of scope.
- Duplicate URLs are treated as intentional repeated requests rather than being
  automatically deduplicated.
