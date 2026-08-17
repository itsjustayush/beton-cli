"""Read-only machine inspection helpers."""

from __future__ import annotations

import platform
import shutil
import subprocess
from pathlib import Path


def find_files(pattern: str, root: Path, limit: int = 50) -> list[Path]:
    """Find matching files below an explicit root with a bounded result count."""
    if not root.exists() or not root.is_dir():
        return []
    results: list[Path] = []
    for path in root.rglob(pattern):
        if path.is_file():
            results.append(path)
            if len(results) >= limit:
                break
    return results


def process_rows(query: str | None = None, limit: int = 50) -> list[list[str]]:
    """Return a bounded, read-only process listing."""
    if platform.system() == "Windows":
        command = ["tasklist", "/FO", "CSV", "/NH"]
        try:
            completed = subprocess.run(command, capture_output=True, text=True, check=True, timeout=5)
        except (OSError, subprocess.SubprocessError):
            return []
        rows: list[list[str]] = []
        for line in completed.stdout.splitlines()[:limit]:
            fields = [field.strip('"') for field in line.split('","')]
            if fields and (not query or query.lower() in fields[0].lower()):
                rows.append(fields[:3])
        return rows

    executable = shutil.which("ps")
    if not executable:
        return []
    try:
        completed = subprocess.run([executable, "-eo", "pid=,comm=,args="], capture_output=True, text=True, check=True, timeout=5)
    except (OSError, subprocess.SubprocessError):
        return []
    rows = []
    for line in completed.stdout.splitlines():
        parts = line.strip().split(None, 2)
        if len(parts) < 2:
            continue
        if query and query.lower() not in line.lower():
            continue
        rows.append(parts[:3])
        if len(rows) >= limit:
            break
    return rows
