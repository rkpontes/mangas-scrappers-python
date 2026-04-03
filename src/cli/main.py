from __future__ import annotations

from enum import Enum
from pathlib import Path
from urllib.parse import urlparse

import typer
from rich.console import Console

from src.lib.http_client import HttpClient
from src.scrapers.extractor import ChapterExtractor
from src.scrapers.models import (
    BatchEntry,
    BatchEntryResult,
    BatchEntryState,
    BatchInputRequest,
    BatchResult,
    BatchSummary,
    FailureReason,
    ResultStatus,
    SaveStatus,
)
from src.services.image_downloader import ImageDownloader
from src.services.path_builder import PathBuilder
from src.services.result_formatter import (
    format_failure_message,
    render_human,
    render_human_batch,
    render_json,
)


app = typer.Typer(help="Extract manga chapter images from public chapter URLs.")
console = Console()


class OutputFormat(str, Enum):
    HUMAN = "human"
    JSON = "json"


def _validate_url(chapter_url: str) -> None:
    parsed = urlparse(chapter_url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise typer.BadParameter("Provide an absolute HTTP or HTTPS chapter URL.")


def _read_batch_entries(target_path: str) -> list[BatchEntry]:
    path = Path(target_path).expanduser()
    try:
        content = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise typer.BadParameter(f"Provide a readable local text file: {exc}") from exc

    entries: list[BatchEntry] = []
    for line_number, raw_value in enumerate(content.splitlines(), start=1):
        entries.append(
            BatchEntry(
                line_number=line_number,
                raw_value=raw_value,
                normalized_value=raw_value.strip(),
            )
        )
    return entries


def _run_single_extract(
    extractor: ChapterExtractor,
    downloader: ImageDownloader | None,
    target: str,
) -> "ChapterResult":
    result = extractor.extract(target)
    if downloader and result.image_entries:
        result = downloader.save(result)
    if result.failure_reason and not result.messages:
        result.add_message(format_failure_message(result.failure_reason))
    return result


def _run_batch_extract(
    request: BatchInputRequest,
    extractor: ChapterExtractor,
    downloader: ImageDownloader | None,
) -> BatchResult:
    entries = _read_batch_entries(request.target_path)
    batch_result = BatchResult(
        target_path=request.target_path,
        summary=BatchSummary(total_lines=len(entries)),
    )

    for entry in entries:
        if not entry.normalized_value:
            entry.entry_state = BatchEntryState.SKIPPED
            batch_result.entries.append(
                BatchEntryResult(
                    line_number=entry.line_number,
                    source_value="",
                    status=SaveStatus.SKIPPED,
                    skip_reason="Blank line skipped.",
                )
            )
            batch_result.summary.skipped_entries += 1
            continue

        batch_result.summary.processed_entries += 1
        try:
            _validate_url(entry.normalized_value)
        except typer.BadParameter as exc:
            entry.entry_state = BatchEntryState.FAILED_VALIDATION
            batch_result.entries.append(
                BatchEntryResult(
                    line_number=entry.line_number,
                    source_value=entry.normalized_value,
                    status=ResultStatus.FAILED,
                    skip_reason=str(exc),
                )
            )
            batch_result.summary.failed_entries += 1
            continue

        entry.entry_state = BatchEntryState.PROCESSED
        chapter_result = _run_single_extract(extractor, downloader, entry.normalized_value)
        batch_result.entries.append(
            BatchEntryResult(
                line_number=entry.line_number,
                source_value=entry.normalized_value,
                status=chapter_result.status,
                chapter_result=chapter_result,
            )
        )
        if chapter_result.status is ResultStatus.SUCCESS:
            batch_result.summary.successful_entries += 1
        else:
            batch_result.summary.failed_entries += 1

    batch_result.add_message("Batch processing completed.")
    return batch_result


@app.callback()
def main() -> None:
    """Root CLI callback."""


@app.command("extract")
def extract(
    target: str,
    file_mode: bool = typer.Option(False, "--file", help="Treat target as a local text file with one chapter URL per line."),
    save: bool = typer.Option(False, "--save", help="Save the extracted images under /contents."),
    output_format: OutputFormat = typer.Option(OutputFormat.HUMAN, "--output-format"),
) -> None:
    http_client = HttpClient()
    try:
        extractor = ChapterExtractor(http_client)
        downloader = ImageDownloader(http_client, PathBuilder()) if save else None

        if file_mode:
            request = BatchInputRequest(target_path=target, save_enabled=save, output_format=output_format.value)
            result = _run_batch_extract(request, extractor, downloader)
        else:
            _validate_url(target)
            result = _run_single_extract(extractor, downloader, target)

        if output_format is OutputFormat.JSON:
            console.print(render_json(result))
        elif file_mode:
            render_human_batch(console, result)
        else:
            render_human(console, result)

        if file_mode:
            has_save_failure = any(
                entry.chapter_result and entry.chapter_result.failure_reason in {FailureReason.SAVE_FAILURE, FailureReason.COLLISION}
                for entry in result.entries
            )
            has_failures = result.summary.failed_entries > 0
            if has_save_failure:
                raise typer.Exit(code=2)
            if has_failures:
                raise typer.Exit(code=1)
        else:
            if result.status is ResultStatus.FAILED:
                raise typer.Exit(code=1)
            if result.failure_reason in {FailureReason.SAVE_FAILURE, FailureReason.COLLISION}:
                raise typer.Exit(code=2)
    finally:
        http_client.close()


def run() -> None:
    app()


if __name__ == "__main__":
    run()
