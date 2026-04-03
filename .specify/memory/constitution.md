<!--
Sync Impact Report
- Version change: template -> 1.0.0
- Modified principles:
  - Principle 1 -> I. Small Scope First
  - Principle 2 -> II. Clean Code by Default
  - Principle 3 -> III. Simple Structure, Simple Flow
  - Principle 4 -> IV. Manual Validation in V1
  - Principle 5 -> V. Explicit Errors and Minimal Dependencies
- Added sections:
  - Operational Constraints
  - Delivery Workflow
- Removed sections:
  - None
- Templates requiring updates:
  - ✅ updated: .specify/templates/plan-template.md
  - ✅ updated: .specify/templates/spec-template.md
  - ✅ updated: .specify/templates/tasks-template.md
  - ✅ no command templates directory present: .specify/templates/commands/
  - ✅ no runtime guidance docs present: README.md, docs/, **/AGENTS.md
- Follow-up TODOs:
  - None
-->
# Mangas Scrappers Constitution

## Core Principles

### I. Small Scope First
Every change MUST keep the project small, focused, and easy to understand.
Features that do not serve the core scraping flow MUST be rejected or deferred.
Each module, file, and function MUST have a single clear purpose. If a feature
requires broad abstractions, generic frameworks, or future-proofing guesses, the
default decision is to simplify or cut scope. Rationale: a small project stays
maintainable only when unnecessary surface area is actively avoided.

### II. Clean Code by Default
Code MUST be written for direct readability, not cleverness. Names MUST explain
intent. Functions SHOULD stay short and do one thing. Conditionals and branching
MUST be flattened when a simpler flow exists. Comments MUST be rare and only
explain non-obvious decisions. Dead code, commented-out code, and unused
configuration MUST be removed. Rationale: the cheapest maintenance path for a
small codebase is code that reads clearly without extra interpretation.

### III. Simple Structure, Simple Flow
The architecture MUST prefer the fewest moving parts that solve the current
problem. Layers, patterns, and abstractions MUST be introduced only when they
remove present complexity, not hypothetical future complexity. Data flow SHOULD
be linear and explicit. Shared utilities MUST remain small and domain-specific.
Rationale: simple structures reduce debugging time and make scraper behavior
predictable.

### IV. Manual Validation in V1
This first version MUST NOT require automated tests as a delivery gate.
Validation MUST happen through explicit manual checks documented in specs, plans,
quickstarts, or task descriptions. Every delivered feature MUST include a clear
way to run and verify it manually. If behavior is hard to validate manually, the
design MUST be simplified before implementation. Rationale: the initial goal is
to reach a working, understandable baseline without expanding the project with a
test harness too early.

### V. Explicit Errors and Minimal Dependencies
Failures MUST be visible and actionable. Errors MUST not be silently ignored.
Logs and messages SHOULD identify what failed, where, and the next useful debug
step. New dependencies MUST be added only when they clearly reduce code
complexity more than they increase project weight. Rationale: scrapers fail in
environmental and data-dependent ways, so diagnosis must stay straightforward.

## Operational Constraints

- The default implementation target is a single small application or CLI.
- New files and modules MUST be added only when they improve clarity.
- Configuration MUST stay minimal and local to the project.
- External services, queues, databases, or background workers MUST NOT be added
  unless the feature cannot exist without them.
- Documentation MUST describe only the current behavior; speculative roadmap
  notes MUST stay out of implementation artifacts.

## Delivery Workflow

- Plans MUST include a constitution check that verifies scope remains small,
  code organization stays simple, manual validation is defined, and dependency
  additions are justified.
- Specifications MUST define independent user stories and describe how each one
  is validated manually in this first version.
- Tasks MUST be split into small, reviewable increments with exact file paths.
- Refactors are allowed only when they reduce present complexity or unblock the
  current feature.
- Automated tests MAY be introduced in a later version of the constitution when
  the project baseline is stable enough to justify them.

## Governance
This constitution overrides conflicting local practices for planning and
implementation. Every plan, spec, and task list MUST be reviewed against these
principles before work starts and again before delivery.

Amendments MUST be recorded in this file with an updated Sync Impact Report and
propagated to affected templates in the same change.

Versioning policy:
- MAJOR for removing or redefining a principle in a backward-incompatible way.
- MINOR for adding a new principle or materially expanding governance.
- PATCH for clarifications, wording improvements, or non-semantic edits.

Compliance review expectations:
- Any added abstraction, dependency, or workflow step MUST be justified against
  the Small Scope First and Simple Structure, Simple Flow principles.
- Any feature proposal that requires automated test infrastructure in v1 MUST
  explicitly justify why manual validation is insufficient.
- Reviews MUST reject changes that increase complexity without immediate value.

**Version**: 1.0.0 | **Ratified**: 2026-04-03 | **Last Amended**: 2026-04-03
