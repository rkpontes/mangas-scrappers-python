# CLI Contract: Manga Chapter Image Extraction

## Purpose

Define the command-line interface exposed to the user for chapter extraction and
optional image saving.

## Command

```text
manga-fetch extract <chapter-url> [--save] [--output-format human|json]
```

## Arguments

- `chapter-url`: Required absolute URL of the manga chapter page to process.

## Options

- `--save`: Download and persist the extracted images under
  `/contents/<manga title>/<chapter label>/<image index>.<image extension>`.
- `--output-format human|json`: Control whether results are rendered for a
  person in the terminal or returned as structured JSON. Default: `human`.

## Human Output Contract

On success, the command prints:
- Source URL or canonical URL
- Source domain
- Compatibility note indicating whether the domain is recommended
- Manga title
- Chapter label
- Ordered page count
- Save summary when `--save` is used

On failure, the command prints:
- Failure status
- Clear reason category: invalid URL, unsupported structure, inaccessible
  content, no images found, or save failure
- Next useful action when possible

## JSON Output Contract

```json
{
  "status": "success|partial|failed",
  "source_url": "string",
  "source_domain": "string",
  "recommended_source": true,
  "manga_title": "string",
  "chapter_label": "string",
  "messages": ["string"],
  "images": [
    {
      "index": 1,
      "image_url": "string",
      "extension": "jpg",
      "output_filename": "1.jpg",
      "saved_path": "/contents/title/chapter/1.jpg",
      "save_status": "saved|skipped|failed"
    }
  ],
  "save_result": {
    "root_path": "/contents",
    "written_files": 12,
    "collisions": [],
    "errors": []
  }
}
```

## Exit Behavior

- Exit `0` when extraction succeeds or partially succeeds with user-visible
  warnings.
- Exit non-zero when input validation fails, extraction cannot proceed, or the
  save operation fails before any useful result is produced.
