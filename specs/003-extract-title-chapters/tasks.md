# Tasks: Title-Based Chapter Extraction

**Input**: Design documents from `/specs/003-extract-title-chapters/`
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

**Purpose**: Prepare planning artifacts and command references for implementation

- [X] T001 Update command examples and manual validation references in /Users/raphaelpontes/Documents/Projetos/Scrappers/mangas-scrappers/AGENTS.md
- [X] T002 Align command references in /Users/raphaelpontes/Documents/Projetos/Scrappers/mangas-scrappers/specs/003-extract-title-chapters/quickstart.md with the final implementation scope

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core CLI and domain changes that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T003 Rename the existing `extract` command to `extract-chapter` in /Users/raphaelpontes/Documents/Projetos/Scrappers/mangas-scrappers/src/cli/main.py
- [X] T004 [P] Add shared title URL parsing and validation helpers in /Users/raphaelpontes/Documents/Projetos/Scrappers/mangas-scrappers/src/lib/text.py
- [X] T005 [P] Extend title-oriented request/result dataclasses and summary models in /Users/raphaelpontes/Documents/Projetos/Scrappers/mangas-scrappers/src/scrapers/models.py
- [X] T006 Add shared CLI helpers for readable file input and direct-vs-file mode orchestration in /Users/raphaelpontes/Documents/Projetos/Scrappers/mangas-scrappers/src/cli/main.py
- [X] T007 Add title discovery support for MangaDex title URLs in /Users/raphaelpontes/Documents/Projetos/Scrappers/mangas-scrappers/src/scrapers/adapters/mangadex.py
- [X] T008 Expose title discovery and chapter de-duplication orchestration in /Users/raphaelpontes/Documents/Projetos/Scrappers/mangas-scrappers/src/scrapers/extractor.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Extract All Chapters from Title Input (Priority: P1) 🎯 MVP

**Goal**: Accept one MangaDex title URL or a file of title URLs and process all discovered chapter URLs through the existing chapter extraction flow

**Independent Validation**: Run `python3 -m src.cli.main extract-title "<mangadex-title-url>"` and `python3 -m src.cli.main extract-title "<file-path>" --file`, then confirm each title is processed and its discovered chapters are attempted sequentially

### Validation for User Story 1 (MANDATORY) ⚠️

- [X] T009 [US1] Document direct title URL and title file validation steps in /Users/raphaelpontes/Documents/Projetos/Scrappers/mangas-scrappers/specs/003-extract-title-chapters/quickstart.md
- [X] T010 [US1] Verify direct title URL, title file input, blank-line skip, invalid title URL, and unreadable file scenarios manually via /Users/raphaelpontes/Documents/Projetos/Scrappers/mangas-scrappers/specs/003-extract-title-chapters/quickstart.md

### Implementation for User Story 1

- [X] T011 [US1] Implement the `extract-title` command entrypoint and title/file mode routing in /Users/raphaelpontes/Documents/Projetos/Scrappers/mangas-scrappers/src/cli/main.py
- [X] T012 [US1] Implement title file parsing, per-line normalization, and duplicate-title preservation in /Users/raphaelpontes/Documents/Projetos/Scrappers/mangas-scrappers/src/cli/main.py
- [X] T013 [US1] Implement title run execution that discovers chapters and reuses chapter extraction per discovered URL in /Users/raphaelpontes/Documents/Projetos/Scrappers/mangas-scrappers/src/cli/main.py
- [X] T014 [US1] Add clear title-level validation and no-chapters-found messages in /Users/raphaelpontes/Documents/Projetos/Scrappers/mangas-scrappers/src/cli/main.py
- [X] T015 [US1] Ensure title discovery returns unique chapter URLs per title in /Users/raphaelpontes/Documents/Projetos/Scrappers/mangas-scrappers/src/scrapers/adapters/mangadex.py

**Checkpoint**: At this point, User Story 1 should be fully functional and manually validatable independently

---

## Phase 4: User Story 2 - Review Chapter-by-Chapter Outcomes (Priority: P2)

**Goal**: Show explicit title-level and chapter-level outcomes, summaries, and exit codes for direct and file-driven title runs

**Independent Validation**: Run `extract-title` with mixed-success titles and confirm the CLI shows per-chapter outcomes, title summaries, aggregate totals, and correct exit-code behavior without stopping after the first failure

### Validation for User Story 2 (MANDATORY)

- [X] T016 [US2] Document mixed-success title run and summary validation steps in /Users/raphaelpontes/Documents/Projetos/Scrappers/mangas-scrappers/specs/003-extract-title-chapters/quickstart.md
- [X] T017 [US2] Verify chapter failure continuation, later-title continuation, and final summary totals manually via /Users/raphaelpontes/Documents/Projetos/Scrappers/mangas-scrappers/specs/003-extract-title-chapters/quickstart.md

### Implementation for User Story 2

- [X] T018 [US2] Implement human-readable rendering for title runs, title entries, and chapter-level outcomes in /Users/raphaelpontes/Documents/Projetos/Scrappers/mangas-scrappers/src/services/result_formatter.py
- [X] T019 [US2] Implement JSON rendering support for title run results in /Users/raphaelpontes/Documents/Projetos/Scrappers/mangas-scrappers/src/services/result_formatter.py
- [X] T020 [US2] Add title summary counting and result-status aggregation in /Users/raphaelpontes/Documents/Projetos/Scrappers/mangas-scrappers/src/cli/main.py
- [X] T021 [US2] Apply title-mode exit code rules for validation, extraction, and partial failure scenarios in /Users/raphaelpontes/Documents/Projetos/Scrappers/mangas-scrappers/src/cli/main.py

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Save Title Extraction Results Predictably (Priority: P3)

**Goal**: Preserve the existing save behavior for every successful chapter discovered from title runs

**Independent Validation**: Run `extract-title "<mangadex-title-url>" --save` and `extract-title "<file-path>" --file --save`, then confirm successful chapters are saved under the existing `contents/` layout and failures do not remove successful outputs

### Validation for User Story 3 (MANDATORY)

- [X] T022 [US3] Document title-save and collision validation steps in /Users/raphaelpontes/Documents/Projetos/Scrappers/mangas-scrappers/specs/003-extract-title-chapters/quickstart.md
- [ ] T023 [US3] Verify successful saves, save collisions, and continued processing after save failures manually via /Users/raphaelpontes/Documents/Projetos/Scrappers/mangas-scrappers/specs/003-extract-title-chapters/quickstart.md

### Implementation for User Story 3

- [X] T024 [US3] Reuse the existing downloader flow for discovered chapters in title runs within /Users/raphaelpontes/Documents/Projetos/Scrappers/mangas-scrappers/src/cli/main.py
- [X] T025 [US3] Surface title-mode save outcomes and save-related failure details in /Users/raphaelpontes/Documents/Projetos/Scrappers/mangas-scrappers/src/services/result_formatter.py
- [X] T026 [US3] Apply save-related exit code propagation for title runs in /Users/raphaelpontes/Documents/Projetos/Scrappers/mangas-scrappers/src/cli/main.py

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T027 [P] Normalize remaining command references from `extract` to `extract-chapter` in /Users/raphaelpontes/Documents/Projetos/Scrappers/mangas-scrappers/specs/001-chapter-image-fetcher/spec.md and /Users/raphaelpontes/Documents/Projetos/Scrappers/mangas-scrappers/specs/002-batch-url-extract/spec.md
- [X] T028 Run `python3 -m py_compile $(find src -name '*.py' | sort)` from /Users/raphaelpontes/Documents/Projetos/Scrappers/mangas-scrappers and resolve any syntax regressions
- [ ] T029 Run the full manual validation checklist in /Users/raphaelpontes/Documents/Projetos/Scrappers/mangas-scrappers/specs/003-extract-title-chapters/quickstart.md and record any fixes in the touched source files

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Starts after Foundational and delivers the MVP title workflow
- **User Story 2 (P2)**: Starts after Foundational and depends on US1 command execution paths being present
- **User Story 3 (P3)**: Starts after Foundational and depends on US1 title orchestration plus the existing chapter save flow

### Within Each User Story

- Manual validation tasks MUST exist before the story is considered complete
- Core command and model wiring comes before output and exit-code refinement
- Title discovery must exist before title execution
- Save integration comes after the title execution path is functional

### Parallel Opportunities

- `T004` and `T005` can run in parallel after `T003`
- `T027` can run in parallel with other late-story work because it only updates documentation references
- Validation documentation tasks can be prepared while implementation is underway, then finalized after behavior lands

---

## Parallel Example: User Story 1

```bash
# Parallel foundational work after command rename:
Task: "Add shared title URL parsing and validation helpers in src/lib/text.py"
Task: "Extend title-oriented request/result dataclasses and summary models in src/scrapers/models.py"

# Parallel late polish/documentation work:
Task: "Normalize remaining command references from `extract` to `extract-chapter` in specs/001-chapter-image-fetcher/spec.md and specs/002-batch-url-extract/spec.md"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Run direct and file-driven title extraction manually
5. Demo the MVP title workflow before expanding output and save refinements

### Incremental Delivery

1. Finish Setup + Foundational so command rename and title primitives exist
2. Add User Story 1 and validate title discovery/execution as the MVP
3. Add User Story 2 and validate summaries, failure continuation, and JSON/human output
4. Add User Story 3 and validate save semantics plus save-related exit codes
5. Finish with syntax validation and a full quickstart run

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is complete:
   - Developer A: User Story 1 command orchestration in `src/cli/main.py`
   - Developer B: User Story 2 rendering in `src/services/result_formatter.py`
   - Developer C: User Story 3 save integration and final documentation polish

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps each task to a user story for traceability
- Each user story is structured to remain manually validatable on its own
- Automated test tasks were intentionally omitted because the spec keeps manual validation as the v1 gate
- Keep edits concentrated in the existing CLI, adapter, model, formatter, and text helper files
