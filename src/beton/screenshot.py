"""Screenshot capture helpers."""

from __future__ import annotations

import platform
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

from .models import ActionResult, ResultStatus


def capture(path: Path | None = None, dry_run: bool = False) -> ActionResult:
    destination = path or (Path.home() / "Pictures" / f"beton-{datetime.now().strftime('%Y%m%d-%H%M%S')}.png")
    system = platform.system()
    if dry_run:
        return ActionResult(ResultStatus.DRY_RUN, f"Would save a screenshot to {destination}.")
    if system == "Darwin":
        args = ["screencapture", str(destination)]
    elif system == "Windows":
        return ActionResult(ResultStatus.UNAVAILABLE, "Windows screenshot capture needs the native screen adapter planned for the next release.")
    elif shutil.which("gnome-screenshot"):
        args = ["gnome-screenshot", "-f", str(destination)]
    elif shutil.which("scrot"):
        args = ["scrot", str(destination)]
    else:
        return ActionResult(ResultStatus.UNAVAILABLE, "No screenshot utility was detected. Install gnome-screenshot or scrot on Linux.")
    if dry_run:
        return ActionResult(ResultStatus.DRY_RUN, f"Would save a screenshot to {destination}.", detail=" ".join(args))
    try:
        destination.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(args, check=True, capture_output=True, timeout=15)
    except (OSError, subprocess.SubprocessError) as exc:
        return ActionResult(ResultStatus.DENIED, f"Could not capture screenshot: {exc}")
    return ActionResult(ResultStatus.SUCCESS, f"Saved screenshot to {destination}.")
