from __future__ import annotations

from abc import ABC, abstractmethod

from src.lib.http_client import HttpClient
from src.scrapers.models import ChapterResult


class SourceAdapter(ABC):
    domain_patterns: tuple[str, ...] = ()

    def matches(self, url: str) -> bool:
        return any(pattern in url for pattern in self.domain_patterns)

    @abstractmethod
    def extract(self, url: str, http_client: HttpClient) -> ChapterResult:
        raise NotImplementedError
