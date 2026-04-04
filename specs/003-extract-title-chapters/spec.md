# Feature Specification: Title-Based Chapter Extraction

**Feature Branch**: `003-extract-title-chapters`  
**Created**: 2026-04-03  
**Status**: Draft  
**Input**: User description: "a idéia agora é passar um titulo tipo: https://mangadex.org/title/aafb046c-9de4-4c3d-990c-6d75b079c0b9/release-that-witch e a aplicação conseguir obter todas as urls de capitulos e extrair as imagens. o comando poderia ser similar a python3 -m src.cli.main extract-title \"https://mangadex.org/title/aafb046c-9de4-4c3d-990c-6d75b079c0b9/release-that-witch\" --save"

## Clarifications

### Session 2026-04-03

- Q: Como o usuário fornece títulos para processamento? → A: O comando `extract-title` deve aceitar tanto uma URL de título única quanto um arquivo texto local com uma URL de título por linha, seguindo o mesmo padrão já usado para capítulos.
- Q: Como a nomenclatura dos comandos deve ficar? → A: O comando atual `extract` passa a se chamar `extract-chapter`, e o novo fluxo de títulos usa `extract-title`.

## User Scenarios & Validation *(mandatory)*

### User Story 1 - Extract All Chapters from Title Input (Priority: P1)

As a user, I want to provide either one MangaDex title URL or a local text file
containing multiple title URLs so the application can collect all chapter URLs
for each title and process entire series without requiring manual chapter URL
gathering.

**Why this priority**: This is the core requested workflow and delivers the main
value by turning a title page into a complete chapter extraction job.

**Independent Validation**: Run `python3 -m src.cli.main extract-title
"<mangadex-title-url>"` with a valid MangaDex title URL and then run
`python3 -m src.cli.main extract-title "<file-path>" --file` with a local text
file containing title URLs, confirming that the application attempts all
discovered chapters for each requested title in the same execution mode.

**Acceptance Scenarios**:

1. **Given** a valid MangaDex title URL with accessible chapters, **When** the
   user starts `extract-title`, **Then** the system discovers the available
   chapter URLs for that title and attempts extraction for each chapter in the
   same run.
2. **Given** a local text file containing multiple valid MangaDex title URLs,
   **When** the user starts `extract-title` in file mode, **Then** the system
   treats each non-empty line as one title request and processes each title in
   the same execution.

---

### User Story 2 - Review Chapter-by-Chapter Outcomes (Priority: P2)

As a user, I want to see the extraction result for each discovered chapter so I
can understand which chapters succeeded, failed, or were skipped during a
title-wide run.

**Why this priority**: Title extraction can involve many chapters, so the user
must be able to inspect outcomes at chapter level instead of receiving one
opaque success or failure.

**Independent Validation**: Run `extract-title` against both a single title URL
and a title input file that produce a mix of successful and unsuccessful
chapter extractions, then confirm that the output identifies the outcome for
each attempted chapter and provides a summary at the end.

**Acceptance Scenarios**:

1. **Given** a title run where at least one chapter extraction fails, **When**
   processing continues, **Then** the system still attempts the remaining
   chapters and reports distinct outcomes for each one.
2. **Given** a completed `extract-title` run started from either a URL or a
   file, **When** the user reviews the output, **Then** the system shows how
   many titles were processed and how many chapters succeeded, failed, or were
   skipped.

---

### User Story 3 - Save Title Extraction Results Predictably (Priority: P3)

As a user, I want to save all successfully extracted chapters from a title run
using the same organization rules as single-chapter extraction so I can manage
the downloaded content without a separate workflow.

**Why this priority**: Reusing the current save behavior keeps the new command
consistent and prevents title-wide extraction from producing unfamiliar output
layout.

**Independent Validation**: Run `python3 -m src.cli.main extract-title
"<mangadex-title-url>" --save` and `python3 -m src.cli.main extract-title
"<file-path>" --file --save`, confirm that successful chapters are written
under the established save structure, and verify that failures do not remove
successful saves.

**Acceptance Scenarios**:

1. **Given** a title run with saving enabled and multiple successful chapters,
   **When** extraction completes, **Then** each successful chapter is stored
   using the same folder and file naming rules already used for single-chapter
   extraction.
2. **Given** a title run where some chapters fail after others succeed, **When**
   the run finishes, **Then** the saved output for successful chapters remains
   available and failed chapters are reported separately.

### Edge Cases

- What happens when the provided URL is not a MangaDex title URL?
- What happens when the provided file path does not exist or cannot be read?
- How does the system handle blank lines in a title input file?
- What happens when the title exists but currently has no accessible chapter
  listings?
- How does the system behave when the same title URL appears more than once in
  a title input file?
- How does the system behave when some discovered chapter URLs are duplicated in
  the title listing for a single title?
- What happens when title metadata is available but one or more chapter pages
  cannot be extracted?
- How does the system behave when the title contains a large number of chapters
  and the run includes a mix of successes and failures?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide a dedicated `extract-title` command for
  title-based extraction.
- **FR-002**: The system MUST provide a dedicated `extract-chapter` command for
  chapter-based extraction, replacing the current generic chapter extraction
  command name.
- **FR-003**: The `extract-title` command MUST accept either a single MangaDex
  title URL or a local text file as input when file mode is explicitly
  requested.
- **FR-004**: The system MUST validate whether a direct title input is a
  properly formed MangaDex title URL before starting title extraction.
- **FR-005**: When file mode is used with `extract-title`, the system MUST
  treat each non-empty line in the file as one title URL request.
- **FR-006**: The system MUST ignore leading and trailing whitespace around
  title inputs read from a file.
- **FR-007**: The system MUST skip blank lines in a title input file without
  treating them as title extraction failures.
- **FR-008**: The system MUST retrieve the chapter URLs associated with each
  provided MangaDex title.
- **FR-009**: The system MUST attempt chapter extraction for every discovered
  chapter URL during the same title run.
- **FR-010**: The system MUST reuse the existing chapter extraction behavior of
  `extract-chapter` for each chapter discovered from a title.
- **FR-011**: The system MUST continue processing remaining chapters after an
  individual chapter extraction failure.
- **FR-012**: When `extract-title` processes a file of title URLs, the system
  MUST continue to the next title after a title-level validation or extraction
  failure.
- **FR-013**: The system MUST report an individual outcome for each discovered
  chapter, including success, failure, or skip status.
- **FR-014**: The system MUST provide a final summary for the title run showing
  how many titles were processed and how many chapters were discovered,
  succeeded, failed, or skipped.
- **FR-015**: When saving is enabled, the system MUST save each successful
  chapter using the same destination and naming rules already used for
  single-chapter extraction.
- **FR-016**: The system MUST preserve successful saved chapters even when
  other chapters or titles in the same title run fail.
- **FR-017**: The system MUST return a clear error when the provided direct
  input is not a valid MangaDex title URL.
- **FR-018**: The system MUST return a clear error when the provided title file
  path cannot be found or read.
- **FR-019**: The system MUST return a clear result when a valid title URL has
  no chapters available for extraction.
- **FR-020**: The system MUST allow duplicate title URLs in a title input file
  and process each occurrence as a separate requested attempt.
- **FR-021**: The system MUST avoid processing the same discovered chapter more
  than once within a single title listing when duplicate chapter URLs are
  returned from the source listing.

### Key Entities *(include if feature involves data)*

- **Title Extraction Request**: A user-submitted request containing either one
  MangaDex title URL or a local file path plus optional save preference for the
  full title run.
- **Title Input File**: A user-provided text file containing title URLs, with
  one intended title request per non-empty line.
- **Title Chapter Listing**: The collection of chapter URLs and identifying
  metadata discovered from the provided title page.
- **Title Chapter Result**: The per-chapter outcome within a title run,
  including chapter identity, extraction status, and any save result visible to
  the user.
- **Title Extraction Summary**: The final totals for processed titles,
  discovered chapters, attempted chapters, successful chapters, failed
  chapters, and skipped chapters shown after the run completes.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A user can start extraction for all chapters of a valid MangaDex
  title from either a single title URL or a local title input file without
  manually collecting individual chapter URLs first.
- **SC-002**: In manual validation with title inputs that have accessible
  chapters, 100% of discovered chapters produce a visible per-chapter outcome
  by the end of the run.
- **SC-003**: In manual validation, a failure on one discovered chapter does
  not prevent later chapters from being attempted in the same title run.
- **SC-004**: In manual validation of title file input, a failure on one title
  does not prevent later titles in the same file from being attempted.
- **SC-005**: When saving is enabled for a valid title run, 100% of successful
  chapter extractions are stored using the same organization pattern already
  used for single-chapter saves.
- **SC-006**: A user can determine from the final output, in under 30 seconds,
  how many titles were processed and how many chapters were discovered,
  succeeded, failed, or skipped.

## Manual Validation Plan *(mandatory for v1 without automated tests)*

- Run `python3 -m src.cli.main extract-title "<mangadex-title-url>"` with a
  valid MangaDex title URL that has multiple chapters.
- Confirm that the application discovers chapter URLs from the title and
  attempts them in one execution.
- Create a local text file containing multiple title URLs and run
  `python3 -m src.cli.main extract-title "<file-path>" --file`.
- Confirm that each non-empty line in the file is treated as one title request
  and that blank lines are skipped.
- Run the same command against an invalid direct URL and confirm that the
  system returns a clear title URL validation error.
- Run the file mode command with a missing or unreadable file path and confirm
  that the system returns a clear file access error.
- Run the command against a valid title URL with no available chapters and
  confirm that the result clearly reports that no chapters were found.
- Run `python3 -m src.cli.main extract-title "<mangadex-title-url>" --save`
  and confirm that successful chapter outputs are saved using the existing
  single-chapter folder structure.
- Run `python3 -m src.cli.main extract-title "<file-path>" --file --save` and
  confirm that successful chapters from multiple titles are saved using the
  same chapter save organization.
- Confirm that failures during one chapter do not stop the remaining discovered
  chapters from being attempted.
- Confirm that failures during one title do not stop later titles from being
  attempted in file mode.
- Confirm that the final output includes totals for processed titles,
  discovered chapters, successful chapters, failed chapters, and skipped
  chapters.

## Assumptions

- First version scope is limited to MangaDex title URLs and does not yet
  include title pages from other sources.
- The user is already allowed to access the MangaDex title and chapter content
  being processed.
- The renamed `extract-chapter` flow and its optional save behavior remain the
  source of truth for per-chapter extraction results.
- Title-wide extraction is executed within a single local command run; remote
  job queues, scheduling, and resumable background processing are out of scope.
- Duplicate title URLs provided by file input are treated as intentional repeat
  requests and are processed once per occurrence.
- Duplicate chapter URLs returned by a single title source are treated as
  duplicate listings rather than intentional repeat requests and are processed
  only once per title run.
