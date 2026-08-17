"""Resolve friendly Beton targets into URL, application, or filesystem actions."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .config import load_config
from .errors import ResolutionError
from .platform.base import is_url


@dataclass(slots=True)
class ResolvedTarget:
    kind: str
    value: str
    display: str


def resolve_target(target: str) -> ResolvedTarget:
    if is_url(target):
        return ResolvedTarget("url", target, target)

    special_paths = {
        "home": Path.home(),
        "downloads": Path.home() / "Downloads",
        "desktop": Path.home() / "Desktop",
        "documents": Path.home() / "Documents",
        "pictures": Path.home() / "Pictures",
    }
    special = special_paths.get(target.lower())
    if special and special.exists():
        return ResolvedTarget("path", str(special), target)

    config = load_config()
    aliases = config.get("aliases", {})
    alias = aliases.get(target.lower())
    if isinstance(alias, dict) and alias.get("kind") and alias.get("value"):
        return ResolvedTarget(str(alias["kind"]), str(alias["value"]), target)

    expanded = Path(target).expanduser()
    if expanded.exists():
        return ResolvedTarget("path", str(expanded), str(expanded))

    if target.startswith((".", "~", "/")) or ":\\" in target:
        raise ResolutionError(f"I couldn't find that path: {target}")

    return ResolvedTarget("app", target, target)
