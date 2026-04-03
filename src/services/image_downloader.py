from __future__ import annotations

from pathlib import Path

from src.lib.http_client import HttpClient
from src.lib.text import ensure_parent
from src.scrapers.models import ChapterResult, FailureReason, ResultStatus, SaveResult, SaveStatus
from src.services.path_builder import PathBuilder


class ImageDownloader:
    def __init__(self, http_client: HttpClient, path_builder: PathBuilder) -> None:
        self.http_client = http_client
        self.path_builder = path_builder

    def save(self, result: ChapterResult) -> ChapterResult:
        chapter_root = self.path_builder.chapter_root(result)
        collisions: list[str] = []
        for entry in result.image_entries:
            built = self.path_builder.build_image_path(result, entry)
            if built.actual_path.exists():
                collisions.append(built.display_path)
            entry.output_filename = built.actual_path.name

        save_result = SaveResult(
            root_path="/contents",
            manga_directory=chapter_root.parent.name,
            chapter_directory=chapter_root.name,
            collisions=collisions,
        )
        result.save_result = save_result

        if collisions:
            result.failure_reason = FailureReason.COLLISION
            result.status = ResultStatus.PARTIAL
            result.add_message("Save aborted because target files already exist.")
            for entry in result.image_entries:
                entry.save_status = SaveStatus.SKIPPED
            return result

        for entry in result.image_entries:
            built = self.path_builder.build_image_path(result, entry)
            try:
                ensure_parent(built.actual_path)
                content = self.http_client.get_bytes(entry.image_url)
                built.actual_path.write_bytes(content)
                entry.saved_path = built.display_path
                entry.output_filename = built.actual_path.name
                entry.save_status = SaveStatus.SAVED
                save_result.written_files += 1
            except Exception as exc:  # noqa: BLE001
                entry.save_status = SaveStatus.FAILED
                save_result.errors.append(str(exc))

        if save_result.errors:
            result.failure_reason = FailureReason.SAVE_FAILURE
            result.status = ResultStatus.PARTIAL
            result.add_message("One or more images could not be saved.")
        return result
