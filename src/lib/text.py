from __future__ import annotations

import re
from pathlib import Path


INVALID_FS_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
MULTISPACE = re.compile(r"\s+")
NUMERIC_PREFIX_RE = re.compile(r"^\d+(?:\.\d+)?[ ._-]+")
CHAPTER_ID_RE = re.compile(
    r"/chapter/(?P<chapter_id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})",
    re.IGNORECASE,
)


def normalize_label(value: str | None, fallback: str) -> str:
    text = (value or "").strip()
    if not text:
        text = fallback
    text = INVALID_FS_CHARS.sub("_", text)
    text = MULTISPACE.sub(" ", text).strip(" .")
    return text or fallback


def safe_extension(value: str | None, fallback: str = "jpg") -> str:
    text = (value or "").strip().lower().lstrip(".")
    if not text:
        return fallback
    if not re.fullmatch(r"[a-z0-9]{2,5}", text):
        return fallback
    return text


def padded_index(index: int) -> str:
    return f"{index:03d}"


def format_chapter_label(chapter_number: str | None, chapter_title: str | None, fallback: str) -> str:
    title = normalize_label(chapter_title, fallback)
    number = _normalize_chapter_number(chapter_number)
    if not number:
        return title

    clean_title = NUMERIC_PREFIX_RE.sub("", title).strip()
    if clean_title:
        return normalize_label(f"{number}.{clean_title}", fallback)
    return normalize_label(number, fallback)


def _normalize_chapter_number(value: str | None) -> str | None:
    text = (value or "").strip()
    if not text:
        return None
    if re.fullmatch(r"\d+", text):
        return f"{int(text):02d}"
    match = re.fullmatch(r"(\d+)\.(\d+)", text)
    if match:
        whole, fraction = match.groups()
        return f"{int(whole):02d}.{fraction}"
    return normalize_label(text, text)


def extract_chapter_id(url: str) -> str | None:
    match = CHAPTER_ID_RE.search(url)
    return match.group("chapter_id") if match else None


def relative_contents_path(manga_title: str, chapter_label: str, filename: str) -> str:
    return f"/contents/{manga_title}/{chapter_label}/{filename}"


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
