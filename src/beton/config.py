"""Local configuration and data paths for Beton."""

from __future__ import annotations

import json
import os
import platform
from pathlib import Path
from typing import Any

from .errors import ConfigurationError

APP_NAME = "beton"
DEFAULT_CONFIG: dict[str, Any] = {
    "browser": "default",
    "search_engine": "google",
    "style": "default",
    "plain": False,
    "aliases": {
        "chrome": {"kind": "app", "value": "chrome"},
        "code": {"kind": "app", "value": "code"},
        "spotify": {"kind": "app", "value": "spotify"},
        "youtube": {"kind": "url", "value": "https://www.youtube.com"},
        "github": {"kind": "url", "value": "https://github.com"},
        "figma": {"kind": "url", "value": "https://www.figma.com"},
    },
}


def data_dir() -> Path:
    """Return Beton’s local data directory, honoring BETON_HOME for testing."""
    override = os.environ.get("BETON_HOME")
    if override:
        return Path(override).expanduser()

    system = platform.system()
    if system == "Windows":
        root = os.environ.get("APPDATA") or str(Path.home() / "AppData" / "Roaming")
        return Path(root) / "Beton"
    if system == "Darwin":
        return Path.home() / "Library" / "Application Support" / "Beton"
    return Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "beton"


def config_path() -> Path:
    return data_dir() / "config.json"


def notes_path() -> Path:
    return data_dir() / "notes.md"


def reminders_path() -> Path:
    return data_dir() / "reminders.json"


def ensure_data_dir() -> Path:
    path = data_dir()
    path.mkdir(parents=True, exist_ok=True)
    return path


def _copy_defaults() -> dict[str, Any]:
    return json.loads(json.dumps(DEFAULT_CONFIG))


def load_config() -> dict[str, Any]:
    path = config_path()
    if not path.exists():
        return _copy_defaults()
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ConfigurationError(f"Could not read configuration at {path}: {exc}") from exc
    config = _copy_defaults()
    if isinstance(raw, dict):
        config.update(raw)
    return config


def save_config(config: dict[str, Any]) -> Path:
    path = config_path()
    try:
        ensure_data_dir()
        path.write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    except OSError as exc:
        raise ConfigurationError(f"Could not write configuration at {path}: {exc}") from exc
    return path


def set_config_value(key: str, value: Any) -> dict[str, Any]:
    config = load_config()
    if key not in DEFAULT_CONFIG:
        raise ConfigurationError(f"Unknown setting '{key}'. Try: browser, search_engine, style, plain")
    config[key] = value
    save_config(config)
    return config
