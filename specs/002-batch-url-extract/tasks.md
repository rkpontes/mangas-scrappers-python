# Tasks: Batch Chapter URL Processing

**Input**: Design documents from `/specs/002-batch-url-extract/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Validation**: In v1, prefer manual validation tasks. Add automated test tasks only if the feature specification explicitly requires them.

**Organization**: Tasks are grouped by user story to enable independent implementation and manual validation of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/` at repository root, with validation notes in `specs/` when needed

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Align feature documentation and command contract with the planned implementation

- [X] T001 Update feature quickstart commands and validation notes in `specs/002-batch-url-extract/quickstart.md`
- [X] T002 Review and finalize the batch command contract wording in `specs/002-batch-url-extract/contracts/extract-batch-file.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core batch-mode structures and CLI input handling that MUST exist before any user story can be completed

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T003 Add batch request/result dataclasses and batch summary enums in `src/scrapers/models.py`
- [X] T004 [P] Add file-mode input validation and line-reading helpers in `src/cli/main.py`
- [X] T005 [P] Extend human and JSON rendering helpers for batch-level output in `src/services/result_formatter.py`
- [X] T006 Wire shared batch execution flow into `extract` command dispatch in `src/cli/main.py`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Process a List of Chapter URLs (Priority: P1) 🎯 MVP

**Goal**: Let the existing `extract` command accept `<file-path> --file` and process all non-empty lines sequentially

**Independent Validation**: Run `python3 -m src.cli.main extract <file-path> --file` with multiple valid URLs and confirm each line is attempted in one execution with ordered visible results

### Validation for User Story 1 (MANDATORY) ⚠️

- [X] T007 [US1] Document the MVP batch validation flow in `specs/002-batch-url-extract/quickstart.md`
- [X] T008 [US1] Verify `python3 -m src.cli.main extract <file-path> --file` manually with a multi-URL text file and record results in `specs/002-batch-url-extract/quickstart.md`

### Implementation for User Story 1

- [X] T009 [P] [US1] Normalize batch file lines into batch entry records in `src/cli/main.py`
- [X] T010 [US1] Implement sequential per-line extraction reuse of `ChapterExtractor` in `src/cli/main.py`
- [X] T011 [US1] Preserve single-URL mode behavior while adding explicit `--file` branching in `src/cli/main.py`

**Checkpoint**: At this point, User Story 1 should be fully functional and manually validatable independently

---

## Phase 4: User Story 2 - Review Per-URL Outcomes (Priority: P2)

**Goal**: Show clear line-by-line success, failure, and skip outcomes plus batch summary counts without stopping on the first bad entry

**Independent Validation**: Run `python3 -m src.cli.main extract <file-path> --file` with blank lines, invalid URLs, unsupported URLs, and valid URLs; confirm later entries still run and the final summary matches the file contents

### Validation for User Story 2 (MANDATORY)

- [X] T012 [US2] Document mixed-success and mixed-failure validation cases in `specs/002-batch-url-extract/quickstart.md`
- [X] T013 [US2] Verify manual mixed-batch behavior and final summary counts in `specs/002-batch-url-extract/quickstart.md`

### Implementation for User Story 2

- [X] T014 [P] [US2] Add per-entry skip, validation-failure, and extraction-failure mapping in `src/cli/main.py`
- [X] T015 [P] [US2] Render per-entry line context and batch totals for human output in `src/services/result_formatter.py`
- [X] T016 [P] [US2] Extend JSON output to include ordered batch entries and summary fields in `src/services/result_formatter.py`
- [X] T017 [US2] Implement batch exit-code handling that preserves full output while signaling failures in `src/cli/main.py`

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Save Batch Results Predictably (Priority: P3)

**Goal**: Reuse the existing `--save` behavior for successful batch entries while keeping failures isolated and visible

**Independent Validation**: Run `python3 -m src.cli.main extract <file-path> --file --save` with valid and failing URLs and confirm successful chapters are written under `contents/` while failed entries remain reported separately

### Validation for User Story 3 (MANDATORY)

- [X] T018 [US3] Document batch save validation and collision scenarios in `specs/002-batch-url-extract/quickstart.md`
- [X] T019 [US3] Verify `python3 -m src.cli.main extract <file-path> --file --save` manually and record expected save outcomes in `specs/002-batch-url-extract/quickstart.md`

### Implementation for User Story 3

- [X] T020 [P] [US3] Reuse `ImageDownloader` per successful batch entry and preserve saved chapter state in `src/cli/main.py`
- [X] T021 [P] [US3] Propagate save collisions and partial save failures into batch summaries in `src/cli/main.py`
- [X] T022 [US3] Surface batch save status details consistently in human and JSON output in `src/services/result_formatter.py`

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final consistency, syntax validation, and documentation alignment across all user stories

- [X] T023 [P] Refresh command examples and feature notes in `AGENTS.md`
- [X] T024 Run syntax validation with `python3 -m py_compile $(find src -name '*.py' | sort)` from the repository root
- [X] T025 Run the full quickstart validation checklist in `specs/002-batch-url-extract/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational completion
- **User Story 2 (Phase 4)**: Depends on Foundational completion and benefits from US1 batch execution flow being present
- **User Story 3 (Phase 5)**: Depends on Foundational completion and on US1 batch execution flow
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - MVP slice
- **User Story 2 (P2)**: Depends on US1 batch execution path existing so results can be reported per entry
- **User Story 3 (P3)**: Depends on US1 batch execution path and reuses existing save behavior per chapter

### Within Each User Story

- Manual validation steps MUST exist before the story is considered complete
- Batch models and command branching come before per-story integration
- Core implementation comes before manual verification
- Each story must remain independently runnable from the CLI

### Parallel Opportunities

- T004 and T005 can run in parallel after T003
- T009 can run in parallel with T007 after the foundational phase
- T014, T015, and T016 can run in parallel once US1 batch execution exists
- T020 and T021 can run in parallel before T022 consolidates output behavior
- T023 can run in parallel with T024 near the end

---

## Parallel Example: User Story 2

```bash
# Prepare mixed-batch reporting work in parallel:
Task: "Add per-entry skip, validation-failure, and extraction-failure mapping in src/cli/main.py"
Task: "Render per-entry line context and batch totals for human output in src/services/result_formatter.py"
Task: "Extend JSON output to include ordered batch entries and summary fields in src/services/result_formatter.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Run the batch file command without `--save`
5. Demo the MVP batch extraction flow

### Incremental Delivery

1. Complete Setup + Foundational
2. Add User Story 1 and validate batch execution
3. Add User Story 2 and validate per-entry failures plus summary output
4. Add User Story 3 and validate `--file --save`
5. Finish with syntax validation and quickstart walkthrough

### Parallel Team Strategy

1. One developer completes Phase 2 foundational CLI/data-model work
2. After foundation:
   - Developer A: User Story 1 execution flow
   - Developer B: User Story 2 output/reporting
   - Developer C: User Story 3 batch save integration

---

## Notes

- [P] tasks = different files, no dependencies on incomplete tasks
- [Story] labels map tasks directly to spec user stories
- No automated test tasks were added because the spec explicitly targets manual validation for v1
- Keep the implementation inside the current CLI, scraper, and formatter modules unless a tiny helper is clearly simpler
