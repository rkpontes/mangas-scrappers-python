from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Callable
from urllib.parse import urlparse

import typer
import httpx
from rich.console import Console

from src.lib.http_client import HttpClient
from src.lib.text import is_mangadex_title_url
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
    TitleChapterResult,
    TitleInputEntry,
    TitleInputRequest,
    TitleResult,
    TitleRunResult,
    TitleRunSummary,
)
from src.services.image_downloader import ImageDownloader
from src.services.path_builder import PathBuilder
from src.services.result_formatter import (
    format_failure_message,
    render_human,
    render_human_batch,
    render_human_title_run,
    render_json,
)


app = typer.Typer(help="Extract manga chapter images from public chapter URLs and MangaDex title URLs.")
console = Console()


class OutputFormat(str, Enum):
    HUMAN = "human"
    JSON = "json"


def _validate_http_url(value: str, kind: str) -> None:
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise typer.BadParameter(f"Provide an absolute HTTP or HTTPS {kind} URL.")


def _validate_chapter_url(chapter_url: str) -> None:
    _validate_http_url(chapter_url, "chapter")


def _validate_title_url(title_url: str) -> None:
    _validate_http_url(title_url, "title")
    if not is_mangadex_title_url(title_url):
        raise typer.BadParameter("Provide a valid MangaDex title URL.")


def _read_text_lines(target_path: str) -> list[tuple[int, str, str]]:
    path = Path(target_path).expanduser()
    try:
        content = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise typer.BadParameter(f"Provide a readable local text file: {exc}") from exc

    entries: list[tuple[int, str, str]] = []
    for line_number, raw_value in enumerate(content.splitlines(), start=1):
        entries.append((line_number, raw_value, raw_value.strip()))
    return entries


def _read_batch_entries(target_path: str) -> list[BatchEntry]:
    return [
        BatchEntry(line_number=line_number, raw_value=raw_value, normalized_value=normalized_value)
        for line_number, raw_value, normalized_value in _read_text_lines(target_path)
    ]


def _read_title_entries(target_path: str) -> list[TitleInputEntry]:
    return [
        TitleInputEntry(line_number=line_number, raw_value=raw_value, normalized_value=normalized_value)
        for line_number, raw_value, normalized_value in _read_text_lines(target_path)
    ]


def _run_single_extract(
    extractor: ChapterExtractor,
    downloader: ImageDownloader | None,
    target: str,
    progress_callback: Callable[[str], None] | None = None,
) -> "ChapterResult":
    if progress_callback:
        progress_callback(f"Extracting chapter: {target}")
    result = extractor.extract(target)
    if downloader and result.image_entries:
        if progress_callback:
            progress_callback(f"Preparing to save {result.chapter_label} ({len(result.image_entries)} pages)")
        result = downloader.save(result, progress_callback=progress_callback)
    if result.failure_reason and not result.messages:
        result.add_message(format_failure_message(result.failure_reason))
    return result


def _run_batch_extract(
    request: BatchInputRequest,
    extractor: ChapterExtractor,
    downloader: ImageDownloader | None,
    progress_callback: Callable[[str], None] | None = None,
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
            _validate_chapter_url(entry.normalized_value)
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
        if progress_callback:
            progress_callback(f"Processing chapter line {entry.line_number}/{len(entries)}")
        chapter_result = _run_single_extract(
            extractor,
            downloader,
            entry.normalized_value,
            progress_callback=progress_callback,
        )
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


def _failed_title_result(source_value: str, message: str, source_line: int | None = None) -> TitleResult:
    result = TitleResult(source_value=source_value, source_line=source_line, status=ResultStatus.FAILED)
    result.add_message(message)
    return result


def _run_title_result(
    extractor: ChapterExtractor,
    downloader: ImageDownloader | None,
    title_url: str,
    source_line: int | None = None,
    progress_callback: Callable[[str], None] | None = None,
) -> TitleResult:
    try:
        if progress_callback:
            progress_callback(f"Discovering chapters for title: {title_url}")
        discovery = extractor.discover_title_chapters(title_url)
    except ValueError as exc:
        return _failed_title_result(title_url, str(exc), source_line=source_line)
    except httpx.HTTPStatusError as exc:
        return _failed_title_result(
            title_url,
            f"HTTP {exc.response.status_code} while retrieving the MangaDex title feed.",
            source_line=source_line,
        )
    except httpx.HTTPError as exc:
        return _failed_title_result(title_url, str(exc), source_line=source_line)
    except Exception as exc:  # noqa: BLE001
        message = str(exc) or "Unexpected title discovery error."
        return _failed_title_result(title_url, message, source_line=source_line)

    title_result = TitleResult(
        source_value=title_url,
        source_line=source_line,
        status=ResultStatus.SUCCESS,
        discovery=discovery,
    )
    if not discovery.chapter_urls:
        title_result.status = ResultStatus.FAILED
        title_result.add_message("No chapters were found for the provided title URL.")
        return title_result

    for chapter_index, chapter_url in enumerate(discovery.chapter_urls, start=1):
        if progress_callback:
            progress_callback(
                f"Processing title '{discovery.title_label}': chapter {chapter_index}/{len(discovery.chapter_urls)}"
            )
        chapter_result = _run_single_extract(
            extractor,
            downloader,
            chapter_url,
            progress_callback=progress_callback,
        )
        title_result.chapter_results.append(
            TitleChapterResult(
                chapter_index=chapter_index,
                source_value=chapter_url,
                status=chapter_result.status,
                chapter_result=chapter_result,
            )
        )

    has_failures = any(entry.status is not ResultStatus.SUCCESS for entry in title_result.chapter_results)
    if has_failures:
        title_result.status = ResultStatus.PARTIAL
        title_result.add_message("One or more discovered chapters failed during extraction.")
    else:
        title_result.add_message("Title processing completed.")
    return title_result


def _update_title_summary(summary: TitleRunSummary, title_result: TitleResult) -> None:
    summary.processed_titles += 1
    if title_result.discovery:
        summary.discovered_chapters += len(title_result.discovery.chapter_urls)
    if title_result.status is ResultStatus.SUCCESS:
        summary.successful_titles += 1
    else:
        summary.failed_titles += 1

    for chapter_entry in title_result.chapter_results:
        if chapter_entry.status is ResultStatus.SUCCESS:
            summary.successful_chapters += 1
        else:
            summary.failed_chapters += 1


def _run_title_extract(
    request: TitleInputRequest,
    extractor: ChapterExtractor,
    downloader: ImageDownloader | None,
    progress_callback: Callable[[str], None] | None = None,
) -> TitleRunResult:
    result = TitleRunResult(target_value=request.target_value, file_mode=request.file_mode)
    if request.file_mode:
        entries = _read_title_entries(request.target_value)
        result.summary.total_lines = len(entries)
        for entry in entries:
            if not entry.normalized_value:
                entry.entry_state = BatchEntryState.SKIPPED
                result.entries.append(
                    TitleResult(
                        source_value="",
                        source_line=entry.line_number,
                        status=SaveStatus.SKIPPED,
                        messages=["Blank line skipped."],
                    )
                )
                result.summary.skipped_titles += 1
                continue

            try:
                _validate_title_url(entry.normalized_value)
            except typer.BadParameter as exc:
                entry.entry_state = BatchEntryState.FAILED_VALIDATION
                failed_result = _failed_title_result(entry.normalized_value, str(exc), source_line=entry.line_number)
                result.entries.append(failed_result)
                _update_title_summary(result.summary, failed_result)
                continue

            entry.entry_state = BatchEntryState.PROCESSED
            if progress_callback:
                progress_callback(f"Processing title line {entry.line_number}/{len(entries)}")
            title_result = _run_title_result(
                extractor,
                downloader,
                entry.normalized_value,
                source_line=entry.line_number,
                progress_callback=progress_callback,
            )
            result.entries.append(title_result)
            _update_title_summary(result.summary, title_result)
    else:
        _validate_title_url(request.target_value)
        title_result = _run_title_result(
            extractor,
            downloader,
            request.target_value,
            progress_callback=progress_callback,
        )
        result.entries.append(title_result)
        _update_title_summary(result.summary, title_result)

    result.add_message("Title processing completed.")
    return result


@app.callback()
def main() -> None:
    """Root CLI callback."""


@app.command("extract-chapter")
def extract_chapter(
    target: str,
    file_mode: bool = typer.Option(False, "--file", help="Treat target as a local text file with one chapter URL per line."),
    save: bool = typer.Option(False, "--save", help="Save the extracted images under /contents."),
    output_format: OutputFormat = typer.Option(OutputFormat.HUMAN, "--output-format"),
) -> None:
    http_client = HttpClient()
    try:
        extractor = ChapterExtractor(http_client)
        downloader = ImageDownloader(http_client, PathBuilder()) if save else None
        progress_callback: Callable[[str], None] | None = None

        if output_format is OutputFormat.HUMAN:
            with console.status("Preparing chapter extraction...", spinner="dots") as status:
                progress_callback = status.update
                if file_mode:
                    request = BatchInputRequest(target_path=target, save_enabled=save, output_format=output_format.value)
                    result = _run_batch_extract(request, extractor, downloader, progress_callback=progress_callback)
                else:
                    _validate_chapter_url(target)
                    result = _run_single_extract(extractor, downloader, target, progress_callback=progress_callback)
                status.update("Rendering chapter results...")
        else:
            if file_mode:
                request = BatchInputRequest(target_path=target, save_enabled=save, output_format=output_format.value)
                result = _run_batch_extract(request, extractor, downloader)
            else:
                _validate_chapter_url(target)
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


@app.command("extract-title")
def extract_title(
    target: str,
    file_mode: bool = typer.Option(False, "--file", help="Treat target as a local text file with one MangaDex title URL per line."),
    save: bool = typer.Option(False, "--save", help="Save the extracted images under /contents."),
    output_format: OutputFormat = typer.Option(OutputFormat.HUMAN, "--output-format"),
) -> None:
    http_client = HttpClient()
    try:
        extractor = ChapterExtractor(http_client)
        downloader = ImageDownloader(http_client, PathBuilder()) if save else None
        request = TitleInputRequest(target_value=target, file_mode=file_mode, save_enabled=save, output_format=output_format.value)
        if output_format is OutputFormat.HUMAN:
            with console.status("Preparing title extraction...", spinner="dots") as status:
                result = _run_title_extract(request, extractor, downloader, progress_callback=status.update)
                status.update("Rendering title results...")
        else:
            result = _run_title_extract(request, extractor, downloader)

        if output_format is OutputFormat.JSON:
            console.print(render_json(result))
        else:
            render_human_title_run(console, result)

        has_save_failure = any(
            chapter_entry.chapter_result
            and chapter_entry.chapter_result.failure_reason in {FailureReason.SAVE_FAILURE, FailureReason.COLLISION}
            for title_entry in result.entries
            for chapter_entry in title_entry.chapter_results
        )
        has_failures = result.summary.failed_titles > 0 or result.summary.failed_chapters > 0
        if has_save_failure:
            raise typer.Exit(code=2)
        if has_failures:
            raise typer.Exit(code=1)
    finally:
        http_client.close()


def run() -> None:
    app()


if __name__ == "__main__":
    run()
