from __future__ import annotations

from urllib.parse import urlparse

import httpx

from src.lib.http_client import HttpClient
from src.scrapers.adapters.base import SourceAdapter
from src.scrapers.adapters.generic import GenericAdapter
from src.scrapers.adapters.mangadex import MangaDexAdapter
from src.scrapers.models import ChapterResult, FailureReason, ResultStatus
from src.services.result_formatter import is_recommended_domain


class ChapterExtractor:
    def __init__(self, http_client: HttpClient, adapters: list[SourceAdapter] | None = None) -> None:
        self.http_client = http_client
        self.adapters = adapters or [MangaDexAdapter(), GenericAdapter()]

    def extract(self, url: str) -> ChapterResult:
        domain = urlparse(url).hostname or ""
        adapter = self._pick_adapter(url)
        try:
            result = adapter.extract(url, self.http_client)
            result.recommended_source = is_recommended_domain(result.source_domain or domain)
            if not result.image_entries:
                result.status = ResultStatus.FAILED
                result.failure_reason = FailureReason.NO_IMAGES_FOUND
                result.add_message("No chapter pages were extracted from the provided URL.")
            elif result.source_domain and not result.recommended_source:
                result.add_message("This source is not in the recommended compatibility list.")
            return result
        except ValueError as exc:
            return self._failed_result(url, domain, FailureReason.UNSUPPORTED_STRUCTURE, str(exc))
        except httpx.HTTPStatusError as exc:
            return self._failed_result(url, domain, FailureReason.INACCESSIBLE_CONTENT, f"HTTP {exc.response.status_code} while fetching the source.")
        except httpx.HTTPError as exc:
            return self._failed_result(url, domain, FailureReason.INACCESSIBLE_CONTENT, str(exc))
        except Exception as exc:  # noqa: BLE001
            message = str(exc) or "Unexpected extraction error."
            if "redirect" in message.lower():
                message = "The URL redirected to a page that does not expose chapter images."
            return self._failed_result(url, domain, FailureReason.UNKNOWN, message)

    def _pick_adapter(self, url: str) -> SourceAdapter:
        for adapter in self.adapters:
            if adapter.matches(url):
                return adapter
        return GenericAdapter()

    def _failed_result(self, url: str, domain: str, reason: FailureReason, message: str) -> ChapterResult:
        result = ChapterResult(
            source_url=url,
            source_domain=domain,
            manga_title="unknown-manga",
            chapter_label="unknown-chapter",
            status=ResultStatus.FAILED,
            recommended_source=is_recommended_domain(domain),
            failure_reason=reason,
        )
        result.add_message(message)
        result.add_message(
            "Only publicly accessible chapter pages are supported in v1; login automation and access-control bypassing are out of scope."
        )
        return result
