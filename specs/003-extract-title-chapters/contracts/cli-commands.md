# CLI Contract: `extract-chapter` and `extract-title`

## Command Shapes

```text
python3 -m src.cli.main extract-chapter <target> [--file] [--save] [--output-format human|json]
python3 -m src.cli.main extract-title <target> [--file] [--save] [--output-format human|json]
```

## Input Modes

| Command | Mode | Primary argument | Required flags | Expected meaning |
|------|------|------------------|----------------|------------------|
| `extract-chapter` | Single chapter | `<target>` | none | Absolute HTTP/HTTPS chapter URL |
| `extract-chapter` | File mode | `<target>` | `--file` | Readable local text file containing one chapter URL per non-empty line |
| `extract-title` | Single title | `<target>` | none | MangaDex title URL |
| `extract-title` | File mode | `<target>` | `--file` | Readable local text file containing one title URL per non-empty line |

## Validation Rules

| Input case | Expected behavior |
|-----------|-------------------|
| `extract-chapter` with non-HTTP direct input | Reject before extraction with a clear chapter URL validation error |
| `extract-chapter --file` with missing or unreadable path | Reject before extraction with a clear file access error |
| `extract-title` with non-MangaDex or malformed direct input | Reject before title discovery with a clear title URL validation error |
| `extract-title --file` with missing or unreadable path | Reject before processing with a clear file access error |
| Any `--file` mode with blank lines | Skip blank lines without treating them as extraction failures |
| `extract-chapter --file` with duplicate chapter URLs | Process each occurrence independently in file order |
| `extract-title --file` with duplicate title URLs | Process each occurrence independently in file order |
| `extract-title` with duplicate chapter URLs returned inside one title listing | Process each unique discovered chapter once for that title |

## Human Output Contract

- `extract-chapter` single mode retains the current chapter-oriented output.
- `extract-chapter --file` retains batch-style per-entry output plus summary
  totals for processed, successful, failed, and skipped entries.
- `extract-title` direct mode shows title identification, per-chapter outcomes,
  and a summary for the processed title.
- `extract-title --file` shows one visible result block per processed title and
  enough detail for the user to inspect chapter-level successes and failures.
- Title mode output ends with final totals for processed titles and discovered,
  successful, failed, and skipped chapters.

## JSON Output Contract

- `extract-chapter` single mode retains the current chapter JSON contract.
- `extract-chapter --file` retains the current batch JSON contract.
- `extract-title` returns a top-level object containing:
- `target_value`
- `file_mode`
- `entries` in input order
- `summary` with title and chapter counters
- `messages` for run-level notes
- Each title entry includes the source value, optional line number, title-level
  messages, discovery details when available, and ordered per-chapter results.
- Each discovered chapter entry includes the existing per-chapter extraction
  payload currently exposed for single chapter execution.

## Save Semantics

- `--save` keeps the same meaning in both commands.
- `extract-title` saves successful discovered chapters using the same
  `contents/` directory structure already used by `extract-chapter`.
- A save failure on one chapter does not prevent later chapters or later titles
  from being attempted.

## Exit Code Expectations

| Scenario | Expected exit code |
|----------|--------------------|
| All processed work succeeds, with no save collision or save failure | `0` |
| One or more titles or chapters fail validation or extraction | `1`, while still rendering all processed outcomes |
| Any processed chapter ends with save collision or save failure | `2`, preserving the current save-related exit-code separation |

## Out of Scope

- Auto-detection of file mode without `--file`
- Title URLs from non-MangaDex sources
- Concurrent title or chapter execution
- Remote manifests, queues, or resumable title jobs
