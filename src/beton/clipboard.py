"""Clipboard helpers with optional local history."""

from __future__ import annotations

import json
import platform
import shutil
import subprocess
from pathlib import Path

from .config import data_dir, ensure_data_dir
from .models import ActionResult, ResultStatus


def _backend() -> tuple[list[str], list[str]] | None:
    if shutil.which("xclip"):
        return ["xclip", "-selection", "clipboard", "-o"], ["xclip", "-selection", "clipboard"]
    if shutil.which("xsel"):
        return ["xsel", "--clipboard", "--output"], ["xsel", "--clipboard", "--input"]
    if platform.system() == "Darwin" and shutil.which("pbpaste"):
        return ["pbpaste"], ["pbcopy"]
    if platform.system() == "Windows":
        return ["powershell", "-NoProfile", "-Command", "Get-Clipboard"], ["powershell", "-NoProfile", "-Command", "Set-Clipboard"]
    return None


def _history_path() -> Path:
    return data_dir() / "clipboard-history.json"


def _save_history(value: str) -> None:
    ensure_data_dir()
    items: list[str] = []
    if _history_path().exists():
        try:
            loaded = json.loads(_history_path().read_text(encoding="utf-8"))
            items = loaded if isinstance(loaded, list) else []
        except (OSError, json.JSONDecodeError):
            items = []
    if value and (not items or items[0] != value):
        items.insert(0, value)
    _history_path().write_text(json.dumps(items[:20], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read_clipboard(full: bool = False, dry_run: bool = False) -> ActionResult:
    backend = _backend()
    if dry_run:
        return ActionResult(ResultStatus.DRY_RUN, "Would read the current text clipboard.")
    if not backend:
        return ActionResult(ResultStatus.UNAVAILABLE, "Clipboard access is unavailable on this system.")
    try:
        completed = subprocess.run(backend[0], capture_output=True, text=True, check=True, timeout=5)
    except (OSError, subprocess.SubprocessError) as exc:
        return ActionResult(ResultStatus.DENIED, f"Could not read clipboard: {exc}")
    value = completed.stdout.rstrip("\n")
    _save_history(value)
    if not full and len(value) > 2000:
        value = value[:2000] + "\n[truncated; use --full to show everything]"
    return ActionResult(ResultStatus.SUCCESS, value or "Clipboard is empty.")


def write_clipboard(value: str, dry_run: bool = False) -> ActionResult:
    backend = _backend()
    if dry_run:
        return ActionResult(ResultStatus.DRY_RUN, "Would set the text clipboard.")
    if not backend:
        return ActionResult(ResultStatus.UNAVAILABLE, "Clipboard access is unavailable on this system.")
    try:
        command = backend[1]
        input_value = value if platform.system() != "Windows" else None
        if platform.system() == "Windows":
            completed = subprocess.run(command + [value], capture_output=True, text=True, check=True, timeout=5)
        else:
            completed = subprocess.run(command, input=input_value, capture_output=True, text=True, check=True, timeout=5)
    except (OSError, subprocess.SubprocessError) as exc:
        return ActionResult(ResultStatus.DENIED, f"Could not write clipboard: {exc}")
    _save_history(value)
    return ActionResult(ResultStatus.SUCCESS, "Clipboard updated.")


def clear_clipboard(dry_run: bool = False) -> ActionResult:
    return write_clipboard("", dry_run)


def clipboard_history() -> list[str]:
    if not _history_path().exists():
        return []
    try:
        value = json.loads(_history_path().read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    return value if isinstance(value, list) else []
