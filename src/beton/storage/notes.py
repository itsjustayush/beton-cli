"""Append-only local Markdown note storage."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from ..config import ensure_data_dir, notes_path


def add_note(text: str, tag: str | None = None) -> Path:
    ensure_data_dir()
    timestamp = datetime.now().astimezone().isoformat(timespec="seconds")
    suffix = f" `#{tag}`" if tag else ""
    entry = f"\n- **{timestamp}**{suffix} — {text.strip()}\n"
    path = notes_path()
    if not path.exists():
        path.write_text("# BETON Notes\n", encoding="utf-8")
    with path.open("a", encoding="utf-8") as handle:
        handle.write(entry)
    return path


def read_notes() -> str:
    path = notes_path()
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def today_notes() -> list[str]:
    today = datetime.now().astimezone().date().isoformat()
    return [line for line in read_notes().splitlines() if today in line]
