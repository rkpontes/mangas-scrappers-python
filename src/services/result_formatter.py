from __future__ import annotations

import json

from rich.console import Console
from rich.table import Table

from src.scrapers.models import BatchResult, ChapterResult, FailureReason, TitleRunResult


RECOMMENDED_DOMAINS = {"mangadex.org"}


def is_recommended_domain(domain: str) -> bool:
    return domain.lower() in RECOMMENDED_DOMAINS


def format_failure_message(reason: FailureReason | None) -> str:
    mapping = {
        FailureReason.INVALID_URL: "Invalid URL: provide an absolute HTTP or HTTPS chapter URL.",
        FailureReason.INVALID_FILE: "Invalid file: provide a readable local text file.",
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


def render_human_batch(console: Console, result: BatchResult) -> None:
    summary = Table(show_header=False, box=None)
    summary.add_row("Batch File", result.target_path)
    summary.add_row("Total Lines", str(result.summary.total_lines))
    summary.add_row("Processed", str(result.summary.processed_entries))
    summary.add_row("Succeeded", str(result.summary.successful_entries))
    summary.add_row("Failed", str(result.summary.failed_entries))
    summary.add_row("Skipped", str(result.summary.skipped_entries))
    console.print(summary)

    if result.messages:
        for message in result.messages:
            console.print(f"- {message}")

    entries = Table(title="Batch Entries")
    entries.add_column("Line")
    entries.add_column("Status")
    entries.add_column("Input")
    entries.add_column("Details")
    for entry in result.entries:
        details = entry.skip_reason or "-"
        if entry.chapter_result:
            details = "; ".join(entry.chapter_result.messages) or entry.chapter_result.chapter_label
        entries.add_row(str(entry.line_number), entry.status.value, entry.source_value or "-", details)
    console.print(entries)


def render_human_title_run(console: Console, result: TitleRunResult) -> None:
    summary = Table(show_header=False, box=None)
    summary.add_row("Input", result.target_value)
    summary.add_row("File Mode", "yes" if result.file_mode else "no")
    summary.add_row("Processed Titles", str(result.summary.processed_titles))
    summary.add_row("Successful Titles", str(result.summary.successful_titles))
    summary.add_row("Failed Titles", str(result.summary.failed_titles))
    summary.add_row("Skipped Titles", str(result.summary.skipped_titles))
    summary.add_row("Discovered Chapters", str(result.summary.discovered_chapters))
    summary.add_row("Successful Chapters", str(result.summary.successful_chapters))
    summary.add_row("Failed Chapters", str(result.summary.failed_chapters))
    summary.add_row("Skipped Chapters", str(result.summary.skipped_chapters))
    if result.file_mode:
        summary.add_row("Total Lines", str(result.summary.total_lines))
    console.print(summary)

    if result.messages:
        for message in result.messages:
            console.print(f"- {message}")

    for entry in result.entries:
        title_table = Table(show_header=False, box=None, title="Title Result")
        title_table.add_row("Source", entry.source_value)
        title_table.add_row("Line", str(entry.source_line or "-"))
        title_table.add_row("Status", entry.status.value)
        if entry.discovery:
            title_table.add_row("Title", entry.discovery.title_label)
            title_table.add_row("Chapters", str(len(entry.discovery.chapter_urls)))
        console.print(title_table)

        discovery_messages = list(entry.discovery.messages) if entry.discovery else []
        for message in discovery_messages + entry.messages:
            console.print(f"- {message}")

        if entry.chapter_results:
            chapters = Table(title="Discovered Chapters")
            chapters.add_column("Index")
            chapters.add_column("Status")
            chapters.add_column("Chapter")
            chapters.add_column("Details")
            for chapter_entry in entry.chapter_results:
                chapter_label = chapter_entry.source_value
                details = "-"
                if chapter_entry.chapter_result:
                    chapter_label = chapter_entry.chapter_result.chapter_label
                    details = "; ".join(chapter_entry.chapter_result.messages) or chapter_entry.chapter_result.source_url
                chapters.add_row(str(chapter_entry.chapter_index), chapter_entry.status.value, chapter_label, details)
            console.print(chapters)


def render_json(result: ChapterResult | BatchResult | TitleRunResult) -> str:
    return json.dumps(result.to_dict(), indent=2, ensure_ascii=True)
