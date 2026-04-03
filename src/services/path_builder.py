from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from src.lib.text import normalize_label, padded_index, relative_contents_path
from src.scrapers.models import ChapterResult, ImageEntry


@dataclass(slots=True)
class BuiltPath:
    actual_path: Path
    display_path: str


class PathBuilder:
    def __init__(self, project_root: Path | None = None) -> None:
        self.project_root = project_root or Path.cwd()
        self.contents_root = self.project_root / "contents"

    def chapter_root(self, result: ChapterResult) -> Path:
        manga_directory = normalize_label(result.manga_title, "unknown-manga")
        chapter_directory = normalize_label(result.chapter_label, "chapter")
        return self.contents_root / manga_directory / chapter_directory

    def build_image_path(self, result: ChapterResult, entry: ImageEntry) -> BuiltPath:
        manga_directory = normalize_label(result.manga_title, "unknown-manga")
        chapter_directory = normalize_label(result.chapter_label, "chapter")
        filename = f"{padded_index(entry.index)}.{entry.extension}"
        actual = self.contents_root / manga_directory / chapter_directory / filename
        display = relative_contents_path(manga_directory, chapter_directory, filename)
        return BuiltPath(actual_path=actual, display_path=display)
