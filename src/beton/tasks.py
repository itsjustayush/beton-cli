"""Local task storage for lightweight productivity workflows."""

from __future__ import annotations

import json
import uuid
from pathlib import Path

from .config import data_dir, ensure_data_dir


def task_path() -> Path:
    return data_dir() / "tasks.json"


def _load() -> list[dict[str, object]]:
    if not task_path().exists():
        return []
    try:
        value = json.loads(task_path().read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    return value if isinstance(value, list) else []


def _save(items: list[dict[str, object]]) -> None:
    ensure_data_dir()
    task_path().write_text(json.dumps(items, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def add_task(text: str) -> dict[str, object]:
    item = {"id": uuid.uuid4().hex[:8], "text": text.strip(), "done": False}
    items = _load()
    items.append(item)
    _save(items)
    return item


def list_tasks(include_done: bool = False) -> list[dict[str, object]]:
    return [item for item in _load() if include_done or not item.get("done")]


def complete_task(identifier: str) -> dict[str, object] | None:
    items = _load()
    for item in items:
        if str(item.get("id")) == identifier:
            item["done"] = True
            _save(items)
            return item
    return None


def cancel_task(identifier: str) -> dict[str, object] | None:
    items = _load()
    for item in items:
        if str(item.get("id")) == identifier:
            item["cancelled"] = True
            _save(items)
            return item
    return None
