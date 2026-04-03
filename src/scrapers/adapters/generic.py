from __future__ import annotations

from urllib.parse import urlparse

from src.lib.html_parser import parse_document, pick_image_urls, pick_title
from src.lib.text import normalize_label, safe_extension
from src.scrapers.adapters.base import SourceAdapter
from src.scrapers.models import ChapterResult, ImageEntry, ResultStatus


class GenericAdapter(SourceAdapter):
    domain_patterns = ()

    def matches(self, url: str) -> bool:
        return True

    def extract(self, url: str, http_client) -> ChapterResult:
        response = http_client.get(url)
        doc = parse_document(response.text)
        image_urls = pick_image_urls(doc, response.url)
        title = pick_title(doc)
        manga_title = normalize_label(title, "unknown-manga")
        chapter_label = normalize_label(title, "chapter")
        entries = [
            ImageEntry(index=index, image_url=image_url, extension=safe_extension(image_url.rsplit(".", 1)[-1]))
            for index, image_url in enumerate(image_urls, start=1)
        ]
        result = ChapterResult(
            source_url=response.url,
            source_domain=urlparse(response.url).hostname or "",
            manga_title=manga_title,
            chapter_label=chapter_label,
            status=ResultStatus.SUCCESS if entries else ResultStatus.FAILED,
            recommended_source=False,
            image_entries=entries,
        )
        if not entries:
            result.add_message("No chapter images were found in the page structure.")
        return result
