from __future__ import annotations

import json
import re
from collections.abc import Iterable
from urllib.parse import urljoin, urlparse

from selectolax.parser import HTMLParser


IMG_KEYWORDS = ("page", "chapter", "manga", "reader")
SCRIPT_URL_RE = re.compile(r'https?://[^"\'\s]+\.(?:jpg|jpeg|png|webp)', re.IGNORECASE)


def parse_document(html: str) -> HTMLParser:
    return HTMLParser(html)


def pick_title(doc: HTMLParser) -> str | None:
    for selector in (
        "meta[property='og:title']",
        "meta[name='twitter:title']",
        "title",
        "h1",
    ):
        node = doc.css_first(selector)
        if node is None:
            continue
        value = node.attributes.get("content") if selector.startswith("meta") else node.text()
        if value and value.strip():
            return value.strip()
    return None


def pick_image_urls(doc: HTMLParser, base_url: str) -> list[str]:
    ranked: list[tuple[int, str]] = []
    seen: set[str] = set()
    for node in doc.css("img"):
        raw_url = node.attributes.get("data-src") or node.attributes.get("src")
        if not raw_url:
            continue
        full_url = urljoin(base_url, raw_url)
        if full_url in seen:
            continue
        score = _score_image(node.attributes, full_url)
        if score <= 0:
            continue
        seen.add(full_url)
        ranked.append((score, full_url))

    if len(ranked) >= 2:
        return [url for _, url in sorted(ranked, key=lambda item: (-item[0], item[1]))]

    script_urls = extract_image_urls_from_scripts(doc)
    merged: list[str] = []
    for url in script_urls:
        full_url = urljoin(base_url, url)
        if full_url not in seen:
            seen.add(full_url)
            merged.append(full_url)
    if merged:
        return merged

    return [url for _, url in ranked]


def extract_image_urls_from_scripts(doc: HTMLParser) -> list[str]:
    matches: list[str] = []
    seen: set[str] = set()
    for node in doc.css("script"):
        text = node.text(separator=" ", strip=True)
        if not text:
            continue
        if "{" in text and "[" in text:
            for url in _walk_json_strings(text):
                if _looks_like_page_image(url) and url not in seen:
                    seen.add(url)
                    matches.append(url)
        for match in SCRIPT_URL_RE.findall(text):
            if match not in seen:
                seen.add(match)
                matches.append(match)
    return matches


def _walk_json_strings(text: str) -> Iterable[str]:
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return []
    queue = [payload]
    results: list[str] = []
    while queue:
        current = queue.pop()
        if isinstance(current, dict):
            queue.extend(current.values())
        elif isinstance(current, list):
            queue.extend(current)
        elif isinstance(current, str):
            results.append(current)
    return results


def _score_image(attributes: dict[str, str], image_url: str) -> int:
    lowered = " ".join(
        [
            image_url.lower(),
            attributes.get("class", "").lower(),
            attributes.get("id", "").lower(),
            attributes.get("alt", "").lower(),
        ]
    )
    path = urlparse(image_url).path.lower()
    if any(keyword in lowered for keyword in IMG_KEYWORDS):
        score = 5
    elif any(token in path for token in ("/data/", "/chapters/", "/pages/")):
        score = 4
    else:
        score = 1

    if any(bad in lowered for bad in ("logo", "avatar", "icon", "banner", "cover", "thumb")):
        score -= 3
    if not _looks_like_page_image(image_url):
        score -= 2
    return score


def _looks_like_page_image(url: str) -> bool:
    return url.lower().split("?")[0].endswith((".jpg", ".jpeg", ".png", ".webp"))
