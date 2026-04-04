# Feature Specification: Manga Chapter Image Extraction

**Feature Branch**: `001-chapter-image-fetcher`  
**Created**: 2026-04-03  
**Status**: Draft  
**Input**: User description: "Create an application that helps obtain manga chapter images from chapter URLs provided by the user, limited to pages and access flows the user is allowed to use."

## Clarifications

### Session 2026-04-03

- Q: Should the first version accept any chapter URL or only an explicit list of supported sites? → A: Accept any chapter URL, but maintain a list of recommended sites for better compatibility, such as mangadex.org.
- Q: Where should extracted images be saved, and how should the folder structure be organized? → A: Save images under `/contents/<manga title>/<chapter label>/<image index>.<image extension>`.

## User Scenarios & Validation *(mandatory)*

### User Story 1 - Extract Chapter Pages (Priority: P1)

As a user, I want to provide a manga chapter URL and receive the ordered list of
chapter images so I can view or save the chapter content I am allowed to access.

**Why this priority**: This is the core value of the feature. Without reliable
image extraction from a supported chapter URL, the application does not solve
the main user problem.

**Independent Validation**: Run the application with a supported chapter URL
that the user is allowed to access, confirm that the result contains an ordered
list of chapter image references, and verify that the first and last pages are
present and correctly sequenced.

**Acceptance Scenarios**:

1. **Given** a supported chapter URL with accessible chapter pages, **When**
   the user submits the URL, **Then** the system returns the chapter title,
   source page, and the ordered list of chapter images.
2. **Given** a supported chapter URL whose chapter contains multiple pages,
   **When** the system completes extraction, **Then** the returned pages remain
   in reading order without duplicates or missing positions.
3. **Given** a chapter URL from a non-recommended site, **When** the user
   submits the URL, **Then** the system still attempts extraction and reports
   clearly whether the source succeeded, failed, or is incompatible.

---

### User Story 2 - Save Extracted Images (Priority: P2)

As a user, I want to save the extracted chapter images to a local destination so
I can review them later without repeating the extraction step.

**Why this priority**: Saving output increases usability, but it depends on the
core extraction flow already working.

**Independent Validation**: Run the application with a supported chapter URL
and a chosen local destination, confirm that image files are written to the
destination under the required folder structure, and verify that filenames
preserve reading order.

**Acceptance Scenarios**:

1. **Given** an extracted chapter with accessible image files, **When** the
   user chooses to save the output locally, **Then** the system stores the
   chapter images under `/contents/<manga title>/<chapter label>/` using a
   predictable numeric sequence and each file's original image extension.
2. **Given** a destination that already contains files with the same names,
   **When** the user requests saving, **Then** the system prevents accidental
   overwrite or asks the user to choose a safe alternative.

---

### User Story 3 - Understand Failures Clearly (Priority: P3)

As a user, I want clear failure messages when a URL cannot be processed so I can
correct the input or understand whether the source is unsupported.

**Why this priority**: Clear failures reduce trial and error and are important
for manual validation in the first version.

**Independent Validation**: Run the application with an invalid URL, an
unsupported source, and a chapter page that has no extractable images; confirm
that each outcome returns a distinct, actionable explanation.

**Acceptance Scenarios**:

1. **Given** an invalid or malformed URL, **When** the user submits it,
   **Then** the system rejects the input with a clear explanation.
2. **Given** a source page the application does not support or cannot read with
   the user's permitted access, **When** extraction is attempted, **Then** the
   system reports that the source is unsupported or inaccessible instead of
   returning incomplete data.

### Edge Cases

- What happens when the chapter URL redirects to a landing page instead of the
  chapter content page?
- How does the system handle chapters where some image references are missing,
  repeated, or returned out of order?
- What happens when the source page loads but no chapter images are available to
  the user through the permitted access flow?
- How does the system behave when the local save destination is unavailable or
  read-only?
- What happens when the user submits a URL from a site outside the recommended
  compatibility list?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST accept a user-provided manga chapter URL as the
  input for extraction.
- **FR-002**: The system MUST validate whether the provided input is a properly
  formed URL before attempting extraction.
- **FR-003**: The system MUST extract the ordered set of chapter image
  references from supported source pages that the user is allowed to access.
- **FR-003a**: The system MUST accept chapter URLs from any domain and attempt
  extraction when the page is reachable through the user's permitted access
  flow.
- **FR-004**: The system MUST return chapter-level metadata that helps identify
  the result, including at least a source reference and chapter label when
  available.
- **FR-005**: The system MUST preserve reading order in the extracted image list.
- **FR-006**: The system MUST allow the user to save extracted chapter images to
  a local destination.
- **FR-006a**: The system MUST save extracted images under the path
  `/contents/<manga title>/<chapter label>/<image index>.<image extension>`.
- **FR-006b**: The system MUST derive `<manga title>` and `<chapter label>` from
  extracted chapter metadata when available and normalize them into safe folder
  names for the filesystem.
- **FR-006c**: The system MUST preserve the detected image file extension when
  writing each saved page.
- **FR-007**: The system MUST prevent silent data loss when saving output,
  including collisions with existing files.
- **FR-008**: The system MUST provide clear error messages for invalid input,
  unsupported sources, inaccessible content, and partial extraction failures.
- **FR-009**: The system MUST expose enough output detail for the user to verify
  whether extraction succeeded without inspecting internal logs.
- **FR-010**: The system MUST operate only on content the user is permitted to
  access and MUST NOT require bypassing advertisements, access controls,
  anti-bot protections, or other monetization or protection mechanisms.
- **FR-011**: The system MUST inform the user when a source cannot be processed
  within these permitted-access constraints.
- **FR-012**: The system MUST provide a maintained list of recommended sites for
  best-effort compatibility guidance, including examples such as `mangadex.org`.
- **FR-013**: The system MUST distinguish between recommended and
  non-recommended sources in user-facing output without blocking extraction
  attempts for non-recommended URLs.

### Key Entities *(include if feature involves data)*

- **Chapter Request**: A user-provided request containing the source URL and any
  save preferences for the extraction attempt.
- **Chapter Result**: The extracted output for a chapter, including source
  reference, chapter label, extraction status, and ordered image entries.
- **Image Entry**: A single page image reference with its reading position and
  save outcome, file extension, and final output filename.
- **Save Destination**: The user-selected local target for writing extracted
  images, rooted at `/contents/` with manga and chapter subfolders.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In manual validation with supported sources, users can start an
  extraction from a chapter URL in under 30 seconds.
- **SC-002**: For supported sources with accessible chapter pages, at least 95%
  of manual validation runs return the complete ordered chapter image set
  without duplicated page positions.
- **SC-003**: In manual validation, 100% of invalid URL submissions return a
  user-visible explanation instead of a silent failure.
- **SC-004**: Users can save a successfully extracted chapter to a local
  destination in a single flow without needing to repeat extraction, with files
  written under `/contents/<manga title>/<chapter label>/`.
- **SC-005**: Users can tell before or during extraction whether a source is in
  the recommended compatibility list and still attempt processing for other
  URLs.

## Manual Validation Plan *(mandatory for v1 without automated tests)*

- Run the application with one supported chapter URL the user is allowed to
  access.
- Run the application with one recommended source URL, such as a MangaDex
  chapter URL, and confirm the compatibility indication is shown correctly.
- Confirm the displayed result includes chapter identification and an ordered
  list of image entries.
- Save the result to a local destination and confirm the written files preserve
  reading order, the expected chapter folder exists, and each file follows the
  `<image index>.<image extension>` naming pattern.
- Run the application with an invalid URL and confirm the user receives a clear
  validation error.
- Run the application with an unsupported or inaccessible source and confirm the
  user receives a clear explanation that no bypassing of access protections is
  performed.
- Run the application with a non-recommended but syntactically valid chapter URL
  and confirm the system attempts extraction before reporting the outcome.

### CLI Note

- The command name for chapter extraction is `extract-chapter`.

## Assumptions

- The primary user is a single operator running the application for personal
  extraction and review of content they are allowed to access.
- First version scope is limited to chapter image extraction and local saving;
  library management, catalog search, and account automation are out of scope.
- The `/contents/` directory is the required root for saved output in v1.
- Supported sources may vary over time, and unsupported sources are expected to
  fail with explicit feedback rather than hidden fallback behavior.
- Recommended sites are compatibility hints, not an exclusive allowlist.
- MangaDex is the initial recommended compatibility reference for manual
  validation and early usage examples.
- The application will only target access flows that are available to the user
  without bypassing monetization, advertisements, access restrictions, or bot
  protections.
