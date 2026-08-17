"""Search-engine URL construction."""

from __future__ import annotations

from urllib.parse import quote_plus

from .errors import ConfigurationError

SEARCH_URLS = {
    "google": "https://www.google.com/search?q={query}",
    "bing": "https://www.bing.com/search?q={query}",
    "duckduckgo": "https://duckduckgo.com/?q={query}",
    "youtube": "https://www.youtube.com/results?search_query={query}",
    "github": "https://github.com/search?q={query}",
    "maps": "https://www.google.com/maps/search/{query}",
}


def build_search_url(query: str, engine: str = "google") -> str:
    key = engine.lower()
    try:
        template = SEARCH_URLS[key]
    except KeyError as exc:
        choices = ", ".join(sorted(SEARCH_URLS))
        raise ConfigurationError(f"Unknown search engine '{engine}'. Choose from: {choices}") from exc
    return template.format(query=quote_plus(query.strip()))
