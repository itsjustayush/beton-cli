"""Timer duration parsing and display helpers."""

from __future__ import annotations

import re

from .errors import ConfigurationError

DURATION_PATTERN = re.compile(r"^\s*(?P<value>\d+(?:\.\d+)?)\s*(?P<unit>s|sec|secs|m|min|mins|h|hr|hrs)?\s*$", re.I)


def parse_duration(value: str) -> int:
    match = DURATION_PATTERN.match(value)
    if not match:
        raise ConfigurationError("Duration must look like 25, 25m, 90s, or 2h.")
    amount = float(match.group("value"))
    unit = (match.group("unit") or "m").lower()
    multiplier = 1 if unit.startswith("s") else 3600 if unit.startswith("h") else 60
    seconds = int(amount * multiplier)
    if seconds <= 0:
        raise ConfigurationError("Duration must be greater than zero.")
    return seconds


def format_duration(seconds: int) -> str:
    minutes, remainder = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{remainder:02d}"
    return f"{minutes:02d}:{remainder:02d}"
