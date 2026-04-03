from __future__ import annotations

from enum import Enum
from urllib.parse import urlparse

import typer
from rich.console import Console

from src.lib.http_client import HttpClient
from src.scrapers.extractor import ChapterExtractor
from src.scrapers.models import FailureReason, ResultStatus
from src.services.image_downloader import ImageDownloader
from src.services.path_builder import PathBuilder
from src.services.result_formatter import format_failure_message, render_human, render_json


app = typer.Typer(help="Extract manga chapter images from public chapter URLs.")
console = Console()


class OutputFormat(str, Enum):
    HUMAN = "human"
    JSON = "json"


def _validate_url(chapter_url: str) -> None:
    parsed = urlparse(chapter_url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise typer.BadParameter("Provide an absolute HTTP or HTTPS chapter URL.")


@app.callback()
def main() -> None:
    """Root CLI callback."""


@app.command("extract")
def extract(
    chapter_url: str,
    save: bool = typer.Option(False, "--save", help="Save the extracted images under /contents."),
    output_format: OutputFormat = typer.Option(OutputFormat.HUMAN, "--output-format"),
) -> None:
    _validate_url(chapter_url)
    http_client = HttpClient()
    try:
        extractor = ChapterExtractor(http_client)
        result = extractor.extract(chapter_url)
        if save and result.image_entries:
            downloader = ImageDownloader(http_client, PathBuilder())
            result = downloader.save(result)

        if result.failure_reason and not result.messages:
            result.add_message(format_failure_message(result.failure_reason))

        if output_format is OutputFormat.JSON:
            console.print(render_json(result))
        else:
            render_human(console, result)

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
