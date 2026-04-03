# CLI Contract: `extract` File Mode

## Command Shape

```text
python3 -m src.cli.main extract <target> [--file] [--save] [--output-format human|json]
```

## Input Modes

| Mode | Primary argument | Required flags | Expected meaning |
|------|------------------|----------------|------------------|
| Single chapter | `<target>` | none | Absolute HTTP/HTTPS chapter URL |
| Batch file | `<target>` | `--file` | Readable local text file containing one chapter URL per non-empty line |

## Validation Rules

| Input case | Expected behavior |
|-----------|-------------------|
| URL mode with non-HTTP target | Reject before extraction with a clear URL validation error |
| File mode with missing or unreadable path | Reject before extraction with a clear file access error |
| File mode with blank lines | Skip blank lines without treating them as extraction failures |
| File mode with duplicate URLs | Process each occurrence independently in file order |

## Human Output Contract

- In single-URL mode, retain the current chapter-oriented output.
- In file mode, show one visible result block per processed URL in file order.
- In file mode, include enough line or entry context for the user to identify
  which input line succeeded, failed, or was skipped.
- End file mode output with summary totals for processed, successful, failed,
  and skipped entries.

## JSON Output Contract

- In single-URL mode, retain the current chapter JSON contract.
- In file mode, return a top-level object containing:
- `target_path`
- `entries` in file order
- `summary` with processed/successful/failed/skipped counters
- `messages` for batch-level notes
- Skipped lines use `status: "skipped"` and include a `skip_reason`
- Each processed entry includes the per-URL extraction payload currently exposed
  for a single chapter result.

## Save Semantics

- `--save` keeps its current meaning in both modes.
- In file mode, each successful chapter save uses the existing `contents/`
  directory structure and collision behavior.
- A save failure on one entry does not prevent later entries from being
  attempted.

## Exit Code Expectations

| Scenario | Expected exit code |
|----------|--------------------|
| All processed entries succeed, with no save collision/failure | `0` |
| One or more entries fail validation or extraction | `1`, while still rendering all per-entry outcomes |
| Any entry ends with save collision or save failure | `2`, preserving the current save-related exit-code separation |

## Out of Scope

- Auto-detection of file mode without `--file`
- Concurrent batch execution
- Remote batch manifests or non-local input sources
