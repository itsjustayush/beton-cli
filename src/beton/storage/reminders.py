"""Local reminder persistence and time parsing."""

from __future__ import annotations

import json
import re
import uuid
from datetime import datetime, timedelta
from pathlib import Path

from ..config import ensure_data_dir, reminders_path
from ..errors import ConfigurationError

_DURATION = re.compile(r"^\s*(\d+(?:\.\d+)?)\s*(s|m|h|d)\s*$", re.I)


def parse_due(value: str) -> datetime:
    match = _DURATION.match(value)
    now = datetime.now().astimezone()
    if match:
        amount = float(match.group(1))
        unit = match.group(2).lower()
        delta = {"s": timedelta(seconds=amount), "m": timedelta(minutes=amount), "h": timedelta(hours=amount), "d": timedelta(days=amount)}[unit]
        return now + delta
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as exc:
        raise ConfigurationError("Reminder time must look like 30m, 2h, 1d, or ISO time such as 2026-08-18T09:00.") from exc
    return parsed.astimezone() if parsed.tzinfo else parsed.astimezone()


def _load() -> list[dict[str, object]]:
    path = reminders_path()
    if not path.exists():
        return []
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ConfigurationError(f"Could not read reminders at {path}: {exc}") from exc
    return value if isinstance(value, list) else []


def _save(items: list[dict[str, object]]) -> None:
    ensure_data_dir()
    reminders_path().write_text(json.dumps(items, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def add_reminder(text: str, due: datetime) -> dict[str, object]:
    item = {"id": uuid.uuid4().hex[:8], "text": text.strip(), "due": due.isoformat(timespec="seconds"), "done": False}
    items = _load()
    items.append(item)
    _save(items)
    return item


def list_reminders(include_done: bool = False) -> list[dict[str, object]]:
    return [item for item in _load() if include_done or not item.get("done")]


def complete_reminder(identifier: str) -> dict[str, object] | None:
    items = _load()
    for item in items:
        if str(item.get("id")) == identifier:
            item["done"] = True
            _save(items)
            return item
    return None


def cancel_reminder(identifier: str) -> dict[str, object] | None:
    items = _load()
    for item in items:
        if str(item.get("id")) == identifier:
            item["cancelled"] = True
            _save(items)
            return item
    return None
