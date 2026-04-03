from __future__ import annotations

import json

from rich.console import Console
from rich.table import Table

from src.scrapers.models import ChapterResult, FailureReason


RECOMMENDED_DOMAINS = {"mangadex.org"}


def is_recommended_domain(domain: str) -> bool:
    return domain.lower() in RECOMMENDED_DOMAINS


def format_failure_message(reason: FailureReason | None) -> str:
    mapping = {
        FailureReason.INVALID_URL: "Invalid URL: provide an absolute HTTP or HTTPS chapter URL.",
        FailureReason.INACCESSIBLE_CONTENT: "The source page is not accessible through the allowed public-access flow.",
        FailureReason.UNSUPPORTED_STRUCTURE: "The source page structure is not currently supported.",
        FailureReason.NO_IMAGES_FOUND: "The page loaded, but no chapter images were found.",
        FailureReason.SAVE_FAILURE: "Extraction succeeded, but saving the images failed.",
        FailureReason.COLLISION: "Saving was blocked because files already exist at the target path.",
        FailureReason.UNKNOWN: "The extraction failed for an unexpected reason.",
        None: "The extraction failed.",
    }
    return mapping[reason]


def render_human(console: Console, result: ChapterResult) -> None:
    summary = Table(show_header=False, box=None)
    summary.add_row("Status", result.status.value)
    summary.add_row("Source", result.source_url)
    summary.add_row("Domain", result.source_domain)
    summary.add_row("Recommended", "yes" if result.recommended_source else "no")
    summary.add_row("Manga", result.manga_title)
    summary.add_row("Chapter", result.chapter_label)
    summary.add_row("Pages", str(len(result.image_entries)))
    console.print(summary)

    if result.messages:
        for message in result.messages:
            console.print(f"- {message}")

    if result.image_entries:
        pages = Table(title="Pages")
        pages.add_column("Index")
        pages.add_column("Image URL")
        pages.add_column("Save")
        for entry in result.image_entries:
            pages.add_row(str(entry.index), entry.image_url, entry.saved_path or entry.save_status.value)
        console.print(pages)

    if result.save_result:
        save = Table(title="Save Summary")
        save.add_column("Field")
        save.add_column("Value")
        save.add_row("Root", result.save_result.root_path)
        save.add_row("Written", str(result.save_result.written_files))
        save.add_row("Collisions", ", ".join(result.save_result.collisions) or "-")
        save.add_row("Errors", ", ".join(result.save_result.errors) or "-")
        console.print(save)


def render_json(result: ChapterResult) -> str:
    return json.dumps(result.to_dict(), indent=2, ensure_ascii=True)
