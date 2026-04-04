# Quickstart: Title-Based Chapter Extraction

## Prerequisites

- Activate the project environment and install the package in editable mode.
- Prepare local text files only when using `--file`.
- Use MangaDex title URLs for `extract-title`.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Run Chapter Extraction

```bash
python3 -m src.cli.main extract-chapter "https://mangadex.org/chapter/<chapter-id>"
```

Expected result:

- The CLI prints chapter metadata and page URLs.
- Failures are shown with explicit error messages.

## Run Chapter Extraction From a File

```bash
python3 -m src.cli.main extract-chapter /absolute/path/to/chapters.txt --file
```

Expected result:

- Each non-empty line is attempted in file order.
- Blank lines are skipped.
- The terminal shows a visible result for each chapter URL plus a final
  summary.

## Run Title Extraction

```bash
python3 -m src.cli.main extract-title "https://mangadex.org/title/<title-id>/<slug>"
```

Expected result:

- The CLI discovers the chapter URLs for the title.
- The CLI processes the discovered chapters sequentially.
- The terminal shows per-chapter outcomes and a summary for the title run.

## Run Title Extraction From a File

```bash
python3 -m src.cli.main extract-title /absolute/path/to/titles.txt --file
```

Expected result:

- Each non-empty line is treated as one title request.
- Blank lines are skipped.
- Duplicate title URLs are processed once per occurrence.
- The terminal shows visible title-level and chapter-level outcomes plus a
  final run summary.

## Run With Saving

```bash
python3 -m src.cli.main extract-title "https://mangadex.org/title/<title-id>/<slug>" --save
python3 -m src.cli.main extract-title /absolute/path/to/titles.txt --file --save
python3 -m src.cli.main extract-chapter /absolute/path/to/chapters.txt --file --save
```

Expected result:

- Successful chapters are written under `contents/<manga>/<chapter>/`.
- Failures remain visible and do not stop later chapters or later titles.
- Existing saved files continue to surface collisions instead of silent
  overwrite.

## Manual Validation Cases

1. Run `extract-chapter` with one valid chapter URL and confirm the existing
   chapter output still works after the command rename.
2. Run `extract-chapter --file` with a file containing at least two valid
   chapter URLs and confirm both are attempted in one execution.
3. Run `extract-title` with one valid MangaDex title URL and confirm that
   multiple chapters are discovered and processed.
4. Run `extract-title --file` with a file containing multiple valid title URLs,
   one blank line, and one duplicate title URL; confirm blank lines are skipped
   and duplicates are still processed as separate inputs.
5. Add one invalid title URL to the title file and confirm later valid titles
   still run.
6. Re-run title and chapter flows with `--save` and confirm successful
   chapters are stored in the existing `contents/` layout.
7. Re-run the same save inputs and confirm collisions are reported instead of
   silently overwriting files.
8. Run the file modes with a missing file path and confirm the CLI returns a
   clear file access error before extraction starts.
9. Run `python3 -m py_compile $(find src -name '*.py' | sort)` after code
   changes to catch syntax regressions.

## Implementation Notes

- `extract-chapter` is the renamed chapter command and preserves the previous
  direct chapter and file-driven chapter behavior.
- `extract-title` accepts either one MangaDex title URL or a local text file
  when `--file` is provided.
- Invalid title URLs, missing files, blank lines, duplicate title lines, and
  titles with no discovered chapters must all remain visible in manual
  validation output.
- Mixed-success title runs must continue after chapter failures and after
  invalid lines in title files.
- Save validation must confirm that successful discovered chapters continue to
  use the existing `contents/<manga>/<chapter>/` layout and that collisions
  still surface clearly.
