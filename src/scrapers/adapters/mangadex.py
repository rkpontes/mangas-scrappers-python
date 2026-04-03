from __future__ import annotations

from urllib.parse import urlparse

from src.lib.text import extract_chapter_id, format_chapter_label, normalize_label, safe_extension
from src.scrapers.adapters.base import SourceAdapter
from src.scrapers.models import ChapterResult, ImageEntry, ResultStatus


API_ROOT = "https://api.mangadex.org"


class MangaDexAdapter(SourceAdapter):
    domain_patterns = ("mangadex.org",)

    def extract(self, url: str, http_client) -> ChapterResult:
        chapter_id = extract_chapter_id(url)
        if not chapter_id:
            raise ValueError("Could not determine the MangaDex chapter id from the URL.")

        chapter_payload = http_client.get_json(f"{API_ROOT}/chapter/{chapter_id}")
        chapter_data = chapter_payload["data"]
        chapter_attributes = chapter_data["attributes"]
        manga_id = self._pick_related_id(chapter_data["relationships"], "manga")
        at_home = http_client.get_json(f"{API_ROOT}/at-home/server/{chapter_id}")
        manga_title = "unknown-manga"
        if manga_id:
            manga_payload = http_client.get_json(f"{API_ROOT}/manga/{manga_id}")
            manga_title = self._pick_title(manga_payload["data"]["attributes"]["title"])

        chapter_number = chapter_attributes.get("chapter") or "chapter"
        chapter_title = chapter_attributes.get("title") or f"Chapter {chapter_number}"
        chapter_label = format_chapter_label(
            chapter_number=chapter_attributes.get("chapter"),
            chapter_title=chapter_title,
            fallback=f"chapter-{chapter_number}",
        )
        image_entries = []
        chapter_info = at_home["chapter"]
        for index, filename in enumerate(chapter_info.get("data", []), start=1):
            image_url = "/".join(
                [
                    at_home["baseUrl"].rstrip("/"),
                    "data",
                    chapter_info["hash"],
                    filename,
                ]
            )
            image_entries.append(
                ImageEntry(
                    index=index,
                    image_url=image_url,
                    extension=safe_extension(filename.rsplit(".", 1)[-1]),
                )
            )

        return ChapterResult(
            source_url=url,
            source_domain=urlparse(url).hostname or "",
            manga_title=normalize_label(manga_title, "mangadex-title"),
            chapter_label=chapter_label,
            status=ResultStatus.SUCCESS if image_entries else ResultStatus.FAILED,
            recommended_source=True,
            image_entries=image_entries,
        )

    def _pick_related_id(self, relationships: list[dict], relationship_type: str) -> str | None:
        for relationship in relationships:
            if relationship.get("type") == relationship_type:
                return relationship.get("id")
        return None

    def _pick_title(self, titles: dict[str, str]) -> str:
        for key in ("en", "pt-br", "pt"):
            if key in titles and titles[key]:
                return titles[key]
        return next(iter(titles.values()), "mangadex-title")
