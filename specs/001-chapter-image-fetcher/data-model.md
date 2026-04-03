# Data Model: Manga Chapter Image Extraction

## Chapter Request

Purpose:
- Represents one user invocation of the extraction flow.

Fields:
- `source_url`: absolute chapter URL provided by the user.
- `save_enabled`: whether image download and file writing should occur.
- `save_root`: output root path, fixed to `/contents` in v1.
- `compatibility_hint`: optional note indicating whether the domain is in the
  recommended list.

Validation rules:
- `source_url` must be a valid absolute HTTP or HTTPS URL.
- `save_root` must resolve to `/contents` for default output behavior.

Relationships:
- Produces one `Chapter Result`.

## Chapter Result

Purpose:
- Represents the extraction outcome for one chapter URL.

Fields:
- `source_url`: canonical URL used after redirects, when available.
- `source_domain`: hostname used for compatibility messaging.
- `manga_title`: extracted series title or safe fallback label.
- `chapter_label`: extracted chapter label or safe fallback label.
- `status`: `success`, `partial`, or `failed`.
- `recommended_source`: boolean compatibility flag.
- `messages`: user-facing status or warning messages.
- `image_entries`: ordered collection of `Image Entry`.

Validation rules:
- `status` must reflect whether all expected image entries were captured.
- `manga_title` and `chapter_label` must be normalizable into safe folder names.
- `image_entries` must remain ordered by reading position.

Relationships:
- Contains many `Image Entry` records.
- Can produce one `Save Result`.

State transitions:
- `started` -> `success`
- `started` -> `partial`
- `started` -> `failed`

## Image Entry

Purpose:
- Represents one extracted chapter page image.

Fields:
- `index`: 1-based reading position.
- `image_url`: absolute image source URL.
- `extension`: detected file extension such as `jpg`, `png`, or `webp`.
- `output_filename`: final filename in the form `<image index>.<extension>`.
- `saved_path`: final written path when saving succeeds.
- `save_status`: `pending`, `saved`, `skipped`, or `failed`.

Validation rules:
- `index` must be unique within a chapter result.
- `image_url` must be absolute and fetchable through the permitted access flow.
- `extension` must be derived from response metadata or URL fallback.

Relationships:
- Belongs to one `Chapter Result`.

## Save Result

Purpose:
- Summarizes file persistence for one chapter.

Fields:
- `root_path`: `/contents`.
- `manga_directory`: safe directory name for the manga.
- `chapter_directory`: safe directory name for the chapter.
- `written_files`: count of successfully written images.
- `collisions`: list of filename collisions detected before writing.
- `errors`: list of save errors encountered.

Validation rules:
- The final path must match `/contents/<manga title>/<chapter label>/`.
- `written_files` cannot exceed the number of image entries.

Relationships:
- Derived from one `Chapter Result`.
