"""Safe filesystem helpers for Beton."""

from __future__ import annotations

import shutil
from pathlib import Path

from .models import ActionResult, ResultStatus


def copy_path(source: Path, destination: Path, dry_run: bool = False) -> ActionResult:
    if dry_run:
        return ActionResult(ResultStatus.DRY_RUN, f"Would copy {source} to {destination}.")
    if not source.exists():
        return ActionResult(ResultStatus.UNAVAILABLE, f"Source does not exist: {source}")
    try:
        destination.parent.mkdir(parents=True, exist_ok=True)
        if source.is_dir():
            shutil.copytree(source, destination, dirs_exist_ok=True)
        else:
            shutil.copy2(source, destination)
    except OSError as exc:
        return ActionResult(ResultStatus.DENIED, f"Could not copy path: {exc}")
    return ActionResult(ResultStatus.SUCCESS, f"Copied {source} to {destination}.")


def move_path(source: Path, destination: Path, dry_run: bool = False) -> ActionResult:
    if dry_run:
        return ActionResult(ResultStatus.DRY_RUN, f"Would move {source} to {destination}.")
    if not source.exists():
        return ActionResult(ResultStatus.UNAVAILABLE, f"Source does not exist: {source}")
    try:
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source), str(destination))
    except OSError as exc:
        return ActionResult(ResultStatus.DENIED, f"Could not move path: {exc}")
    return ActionResult(ResultStatus.SUCCESS, f"Moved {source} to {destination}.")


def rename_path(source: Path, name: str, dry_run: bool = False) -> ActionResult:
    return move_path(source, source.with_name(name), dry_run)


def trash_path(source: Path, dry_run: bool = False) -> ActionResult:
    trash = Path.home() / ".local" / "share" / "Trash" / "files"
    if dry_run:
        return ActionResult(ResultStatus.DRY_RUN, f"Would move {source} to the system trash.")
    if not source.exists():
        return ActionResult(ResultStatus.UNAVAILABLE, f"Path does not exist: {source}")
    try:
        trash.mkdir(parents=True, exist_ok=True)
        destination = trash / source.name
        counter = 1
        while destination.exists():
            destination = trash / f"{source.stem}.{counter}{source.suffix}"
            counter += 1
        shutil.move(str(source), str(destination))
    except OSError as exc:
        return ActionResult(ResultStatus.DENIED, f"Could not move path to trash: {exc}")
    return ActionResult(ResultStatus.SUCCESS, f"Moved {source} to trash.")
