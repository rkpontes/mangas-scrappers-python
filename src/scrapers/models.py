from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class ResultStatus(str, Enum):
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"


class SaveStatus(str, Enum):
    PENDING = "pending"
    SAVED = "saved"
    SKIPPED = "skipped"
    FAILED = "failed"


class FailureReason(str, Enum):
    INVALID_URL = "invalid_url"
    INVALID_FILE = "invalid_file"
    INACCESSIBLE_CONTENT = "inaccessible_content"
    UNSUPPORTED_STRUCTURE = "unsupported_structure"
    NO_IMAGES_FOUND = "no_images_found"
    SAVE_FAILURE = "save_failure"
    COLLISION = "collision"
    UNKNOWN = "unknown"


class BatchEntryState(str, Enum):
    SKIPPED = "skipped"
    QUEUED = "queued"
    PROCESSED = "processed"
    FAILED_VALIDATION = "failed_validation"


@dataclass(slots=True)
class ImageEntry:
    index: int
    image_url: str
    extension: str
    output_filename: str = ""
    saved_path: str | None = None
    save_status: SaveStatus = SaveStatus.PENDING

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["save_status"] = self.save_status.value
        return payload


@dataclass(slots=True)
class SaveResult:
    root_path: str
    manga_directory: str
    chapter_directory: str
    written_files: int = 0
    collisions: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class ChapterResult:
    source_url: str
    source_domain: str
    manga_title: str
    chapter_label: str
    status: ResultStatus
    recommended_source: bool
    messages: list[str] = field(default_factory=list)
    image_entries: list[ImageEntry] = field(default_factory=list)
    failure_reason: FailureReason | None = None
    save_result: SaveResult | None = None

    def add_message(self, message: str) -> None:
        if message not in self.messages:
            self.messages.append(message)

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status.value,
            "source_url": self.source_url,
            "source_domain": self.source_domain,
            "recommended_source": self.recommended_source,
            "manga_title": self.manga_title,
            "chapter_label": self.chapter_label,
            "messages": self.messages,
            "failure_reason": self.failure_reason.value if self.failure_reason else None,
            "images": [item.to_dict() for item in self.image_entries],
            "save_result": self.save_result.to_dict() if self.save_result else None,
        }


@dataclass(slots=True)
class ChapterRequest:
    source_url: str
    save_enabled: bool = False
    save_root: Path = Path("contents")
    compatibility_hint: str | None = None


@dataclass(slots=True)
class BatchInputRequest:
    target_path: str
    save_enabled: bool = False
    output_format: str = "human"


@dataclass(slots=True)
class BatchEntry:
    line_number: int
    raw_value: str
    normalized_value: str
    entry_state: BatchEntryState = BatchEntryState.QUEUED

    def to_dict(self) -> dict[str, Any]:
        return {
            "line_number": self.line_number,
            "raw_value": self.raw_value,
            "normalized_value": self.normalized_value,
            "entry_state": self.entry_state.value,
        }


@dataclass(slots=True)
class BatchEntryResult:
    line_number: int
    source_value: str
    status: ResultStatus | SaveStatus
    skip_reason: str | None = None
    chapter_result: ChapterResult | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "line_number": self.line_number,
            "source_value": self.source_value,
            "status": self.status.value,
            "skip_reason": self.skip_reason,
            "chapter_result": self.chapter_result.to_dict() if self.chapter_result else None,
        }


@dataclass(slots=True)
class BatchSummary:
    total_lines: int = 0
    processed_entries: int = 0
    successful_entries: int = 0
    failed_entries: int = 0
    skipped_entries: int = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class BatchResult:
    target_path: str
    entries: list[BatchEntryResult] = field(default_factory=list)
    summary: BatchSummary = field(default_factory=BatchSummary)
    messages: list[str] = field(default_factory=list)

    def add_message(self, message: str) -> None:
        if message not in self.messages:
            self.messages.append(message)

    def to_dict(self) -> dict[str, Any]:
        return {
            "target_path": self.target_path,
            "entries": [entry.to_dict() for entry in self.entries],
            "summary": self.summary.to_dict(),
            "messages": self.messages,
        }
