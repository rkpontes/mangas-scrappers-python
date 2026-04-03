from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx


DEFAULT_HEADERS = {
    "User-Agent": "mangas-scrappers/0.1.0",
    "Accept": "*/*",
}


@dataclass(slots=True)
class HttpResponse:
    url: str
    status_code: int
    text: str
    headers: dict[str, str]

    def json(self) -> Any:
        return httpx.Response(
            status_code=self.status_code,
            headers=self.headers,
            text=self.text,
        ).json()


class HttpClient:
    def __init__(self, timeout: float = 20.0) -> None:
        self._client = httpx.Client(
            timeout=timeout,
            follow_redirects=True,
            headers=DEFAULT_HEADERS,
        )

    def close(self) -> None:
        self._client.close()

    def get(self, url: str, headers: dict[str, str] | None = None) -> HttpResponse:
        response = self._client.get(url, headers=headers)
        response.raise_for_status()
        return HttpResponse(
            url=str(response.url),
            status_code=response.status_code,
            text=response.text,
            headers=dict(response.headers),
        )

    def get_json(self, url: str, headers: dict[str, str] | None = None) -> Any:
        response = self._client.get(url, headers=headers)
        response.raise_for_status()
        return response.json()

    def get_bytes(self, url: str, headers: dict[str, str] | None = None) -> bytes:
        response = self._client.get(url, headers=headers)
        response.raise_for_status()
        return response.content
