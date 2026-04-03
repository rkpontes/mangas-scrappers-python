# Quickstart: Batch Chapter URL Processing

## Prerequisites

- Activate the project environment and install the package in editable mode.
- Prepare a local text file with one chapter URL per non-empty line.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Run Batch Extraction

```bash
python3 -m src.cli.main extract /absolute/path/to/chapters.txt --file
```

Expected result:

- Each non-empty line is attempted in file order.
- Blank lines are skipped.
- The terminal shows a visible outcome for each processed URL plus a final
  summary.

## Run Batch Extraction With Saving

```bash
python3 -m src.cli.main extract /absolute/path/to/chapters.txt --file --save
```

Expected result:

- Successful chapters are written under `contents/<manga>/<chapter>/`.
- Failures remain visible and do not prevent later entries from being
  attempted.
- The final summary shows how many entries succeeded, failed, or were skipped.

## Manual Validation Cases

1. Create a file with at least two valid chapter URLs and confirm both are
   attempted in one execution.
2. Add blank lines and a duplicate URL to the file and confirm blank lines are
   skipped while duplicates are still processed.
3. Add one invalid or unsupported URL and confirm later valid URLs still run.
4. Re-run with `--save` and confirm successful chapters are stored in the
   existing `contents/` layout.
5. Re-run the same `--file --save` input and confirm existing saved files are
   reported as collisions instead of being silently overwritten.
6. Run the command with a missing file path and confirm the CLI returns a clear
   file access error before extraction starts.
7. Run `python3 -m py_compile $(find src -name '*.py' | sort)` after code
   changes to catch syntax regressions.
