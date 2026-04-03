# Quickstart: Manga Chapter Image Extraction

## Goal

Manually validate the first version of the CLI that extracts chapter images and
saves them under `/contents`.

## Preconditions

- Python 3.12 is installed.
- Project dependencies are installed.
- The target chapter page is publicly accessible to the user.
- The chapter page is not blocked by login, cookies, or access protections.

## Setup

Install dependencies and verify the CLI help output:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
python3 -m src.cli.main --help
```

## Validation Steps

### 1. Extract a recommended source

Run the CLI against a recommended public source such as a MangaDex chapter URL.

```bash
python3 -m src.cli.main extract "https://mangadex.org/chapter/<chapter-id>"
```

Expected result:
- The command reports `success` or `partial`.
- The output shows source domain, compatibility note, manga title, chapter
  label, and ordered page count.

### 2. Save extracted images

Run the same extraction with `--save`.

```bash
python3 -m src.cli.main extract "https://mangadex.org/chapter/<chapter-id>" --save
```

Expected result:
- The command writes files under
  `/contents/<manga title>/<chapter label>/<image index>.<image extension>`.
- The first page file and last page file both exist.
- Filenames are sequential and preserve the detected image extension.

### 3. Validate invalid URL handling

Run the command with an invalid URL string.

```bash
python3 -m src.cli.main extract "invalid-url"
```

Expected result:
- The command exits non-zero.
- The output states that the URL is invalid and no extraction was attempted.

### 4. Validate unsupported or incompatible source handling

Run the command with a public chapter URL from a non-recommended or unsupported
source.

```bash
python3 -m src.cli.main extract "https://example.com/chapter/test"
```

Expected result:
- The command attempts extraction.
- The output explains whether the source failed due to incompatible page
  structure, inaccessible content, or missing image entries.

### 5. Validate save collision handling

Run the same save command twice for the same chapter.

```bash
python3 -m src.cli.main extract "https://mangadex.org/chapter/<chapter-id>" --save
python3 -m src.cli.main extract "https://mangadex.org/chapter/<chapter-id>" --save
```

Expected result:
- The command does not silently overwrite existing files.
- The output clearly reports collisions or asks for a safe next step.
