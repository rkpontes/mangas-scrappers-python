---

description: "Task list for manga chapter image extraction feature"
---

# Tasks: Manga Chapter Image Extraction

**Input**: Design documents from `/specs/001-chapter-image-fetcher/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Validation**: In v1, prefer manual validation tasks. Add automated test tasks only if the feature specification explicitly requires them.

**Organization**: Tasks are grouped by user story to enable independent implementation and manual validation of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/` at repository root, with validation notes in `specs/` when needed
- Paths below follow the structure defined in `plan.md`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create the project directories from the plan in `src/cli/`, `src/scrapers/adapters/`, `src/services/`, and `src/lib/`
- [x] T002 Initialize the Python project configuration and dependencies in `pyproject.toml`
- [x] T003 [P] Add package markers in `src/__init__.py`, `src/cli/__init__.py`, `src/scrapers/__init__.py`, `src/scrapers/adapters/__init__.py`, `src/services/__init__.py`, and `src/lib/__init__.py`
- [x] T004 [P] Create the CLI entrypoint skeleton in `src/cli/main.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T005 Create shared extraction data models in `src/scrapers/models.py`
- [x] T006 [P] Implement HTTP fetching helpers with timeouts and redirect handling in `src/lib/http_client.py`
- [x] T007 [P] Implement HTML parsing helpers for image and metadata selection in `src/lib/html_parser.py`
- [x] T008 [P] Implement text normalization helpers for safe folder and filename generation in `src/lib/text.py`
- [x] T009 Define the adapter interface and compatibility contract in `src/scrapers/adapters/base.py`
- [x] T010 Implement output path construction for `/contents/<manga title>/<chapter label>/<image index>.<image extension>` in `src/services/path_builder.py`
- [x] T011 Implement shared result rendering for human and JSON output in `src/services/result_formatter.py`
- [x] T012 Implement the extraction orchestrator that selects adapters and assembles `Chapter Result` in `src/scrapers/extractor.py`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Extract Chapter Pages (Priority: P1) 🎯 MVP

**Goal**: Accept a chapter URL and return ordered image entries with chapter metadata

**Independent Validation**: Run `manga-fetch extract <chapter-url>` with a recommended public source and confirm the output includes source domain, compatibility note, manga title, chapter label, and ordered page entries.

### Validation for User Story 1 (MANDATORY) ⚠️

- [x] T013 [US1] Update manual extraction validation steps in `specs/001-chapter-image-fetcher/quickstart.md`
- [ ] T014 [US1] Manually validate happy path extraction and incompatible-source behavior using `specs/001-chapter-image-fetcher/quickstart.md`

### Implementation for User Story 1

- [x] T015 [P] [US1] Implement generic public-page extraction heuristics in `src/scrapers/adapters/generic.py`
- [x] T016 [P] [US1] Implement MangaDex-specific extraction rules in `src/scrapers/adapters/mangadex.py`
- [x] T017 [US1] Integrate adapter registration and fallback selection in `src/scrapers/extractor.py`
- [x] T018 [US1] Implement the extract command flow and URL validation in `src/cli/main.py`
- [x] T019 [US1] Add compatibility messaging for recommended vs non-recommended sources in `src/services/result_formatter.py`
- [x] T020 [US1] Add explicit extraction error mapping for invalid URL, inaccessible content, unsupported structure, and no images found in `src/scrapers/extractor.py`

**Checkpoint**: At this point, User Story 1 should be fully functional and manually validatable independently

---

## Phase 4: User Story 2 - Save Extracted Images (Priority: P2)

**Goal**: Persist extracted chapter images under the required `/contents` folder structure

**Independent Validation**: Run `manga-fetch extract <chapter-url> --save` and confirm files are created in `/contents/<manga title>/<chapter label>/` with sequential filenames preserving the original extension.

### Validation for User Story 2 (MANDATORY)

- [x] T021 [US2] Update save-flow and collision validation steps in `specs/001-chapter-image-fetcher/quickstart.md`
- [ ] T022 [US2] Manually validate save success, folder naming, and collision handling using `specs/001-chapter-image-fetcher/quickstart.md`

### Implementation for User Story 2

- [x] T023 [P] [US2] Implement image download and extension resolution in `src/services/image_downloader.py`
- [x] T024 [US2] Implement `/contents` directory creation and safe chapter path handling in `src/services/path_builder.py`
- [x] T025 [US2] Integrate save execution and `Save Result` assembly in `src/services/image_downloader.py`
- [x] T026 [US2] Wire the `--save` option into the CLI command flow in `src/cli/main.py`
- [x] T027 [US2] Add collision detection and non-destructive save errors to the save workflow in `src/services/image_downloader.py`

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Understand Failures Clearly (Priority: P3)

**Goal**: Return distinct, actionable failure messages for invalid or unsuccessful extraction attempts

**Independent Validation**: Run the CLI with an invalid URL, a non-recommended incompatible source, and a source with missing images; confirm each outcome produces a distinct user-facing explanation and correct exit behavior.

### Validation for User Story 3 (MANDATORY)

- [x] T028 [US3] Update failure-mode validation coverage in `specs/001-chapter-image-fetcher/quickstart.md`
- [ ] T029 [US3] Manually validate invalid URL, unsupported structure, inaccessible content, and save failure scenarios using `specs/001-chapter-image-fetcher/quickstart.md`

### Implementation for User Story 3

- [x] T030 [P] [US3] Add structured failure reason categories and message builders in `src/services/result_formatter.py`
- [x] T031 [P] [US3] Add partial-result and failure-state handling in `src/scrapers/models.py`
- [x] T032 [US3] Implement non-zero exit behavior and warning/success exit rules in `src/cli/main.py`
- [x] T033 [US3] Normalize save and extraction failures into user-visible messages in `src/services/image_downloader.py`
- [x] T034 [US3] Refine extractor failure reporting for redirect-to-landing-page and missing-image edge cases in `src/scrapers/extractor.py`

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T035 [P] Document installation and run commands in `/Users/raphaelpontes/Documents/Projetos/Scrappers/mangas-scrappers/AGENTS.md`
- [x] T036 Code cleanup and simplification across `src/cli/main.py`, `src/scrapers/`, and `src/services/`
- [x] T037 [P] Update compatibility guidance and recommended-site notes in `specs/001-chapter-image-fetcher/spec.md`
- [ ] T038 Run the full manual validation checklist and sync final expected behavior in `specs/001-chapter-image-fetcher/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel if staffed
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Depends functionally on extraction output from US1
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Depends on extraction and save flows from US1/US2 for complete failure coverage

### Within Each User Story

- Manual validation steps MUST exist before the story is considered complete
- Foundational models and helpers before story-specific integrations
- Adapters before CLI orchestration for extraction
- Save services before save CLI integration
- Story complete before moving to next priority when working sequentially

### Parallel Opportunities

- T003 and T004 can run in parallel after T002
- T006, T007, and T008 can run in parallel after T005
- T015 and T016 can run in parallel during US1
- T023 and T024 can run in parallel during US2
- T030 and T031 can run in parallel during US3
- T035 and T037 can run in parallel during Polish

---

## Parallel Example: User Story 1

```bash
# Launch source adapter work in parallel:
Task: "Implement generic public-page extraction heuristics in src/scrapers/adapters/generic.py"
Task: "Implement MangaDex-specific extraction rules in src/scrapers/adapters/mangadex.py"
```

## Parallel Example: User Story 2

```bash
# Launch save-path and downloader work in parallel:
Task: "Implement image download and extension resolution in src/services/image_downloader.py"
Task: "Implement /contents directory creation and safe chapter path handling in src/services/path_builder.py"
```

## Parallel Example: User Story 3

```bash
# Launch failure-shape and message work in parallel:
Task: "Add structured failure reason categories and message builders in src/services/result_formatter.py"
Task: "Add partial-result and failure-state handling in src/scrapers/models.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Validate extraction behavior independently
5. Demo the CLI with a recommended public source

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Validate independently → MVP ready
3. Add User Story 2 → Validate independently → Save flow ready
4. Add User Story 3 → Validate independently → Failure reporting ready
5. Finish Polish → Final manual validation pass

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 extraction adapters and CLI flow
   - Developer B: User Story 2 save pipeline
   - Developer C: User Story 3 failure classification and output behavior
3. Merge stories after each independent validation checkpoint

---

## Notes

- All tasks follow the required checklist format with IDs, optional `[P]`, story labels where applicable, and exact file paths
- Manual validation is the delivery gate for v1
- MVP scope is Phase 3 / User Story 1 only
- Keep the implementation within public-access constraints and without login automation
