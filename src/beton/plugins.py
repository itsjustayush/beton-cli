"""Local plugin registry for optional integrations."""

from __future__ import annotations

import json
from pathlib import Path

from .config import data_dir, ensure_data_dir


def plugin_path() -> Path:
    return data_dir() / "plugins.json"


def list_plugins() -> list[dict[str, object]]:
    path = plugin_path()
    if not path.exists():
        return []
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    return value if isinstance(value, list) else []


def set_plugin(name: str, enabled: bool) -> dict[str, object]:
    plugins = list_plugins()
    existing = next((item for item in plugins if item.get("name") == name), None)
    if existing is None:
        existing = {"name": name, "enabled": enabled, "permissions": []}
        plugins.append(existing)
    else:
        existing["enabled"] = enabled
    ensure_data_dir()
    plugin_path().write_text(json.dumps(plugins, indent=2) + "\n", encoding="utf-8")
    return existing
