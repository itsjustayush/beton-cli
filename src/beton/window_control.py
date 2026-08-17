"""Best-effort desktop window controls."""

from __future__ import annotations

import platform
import shutil
import subprocess

from .models import ActionResult, ResultStatus


def active_window(dry_run: bool = False) -> ActionResult:
    system = platform.system()
    if system == "Darwin":
        args = ["osascript", "-e", 'tell application "System Events" to get name of first application process whose frontmost is true']
    elif system == "Windows":
        args = ["powershell", "-NoProfile", "-Command", "(Get-Process | Where-Object {$_.MainWindowTitle}).MainWindowTitle"]
    elif shutil.which("xdotool"):
        args = ["sh", "-c", "xdotool getactivewindow getwindowname"]
    else:
        return ActionResult(ResultStatus.UNAVAILABLE, "Active-window information is unavailable. Install xdotool on Linux.")
    if dry_run:
        return ActionResult(ResultStatus.DRY_RUN, "Would read the active window.", detail=" ".join(args))
    try:
        completed = subprocess.run(args, capture_output=True, text=True, check=True, timeout=8)
    except (OSError, subprocess.SubprocessError) as exc:
        return ActionResult(ResultStatus.DENIED, f"Could not read the active window: {exc}")
    return ActionResult(ResultStatus.SUCCESS, "Active window", detail=completed.stdout.strip())


def focus_window(title: str, dry_run: bool = False) -> ActionResult:
    system = platform.system()
    if system == "Darwin":
        args = ["osascript", "-e", f'tell application "System Events" to set frontmost of process "{title}" to true']
    elif system == "Windows":
        args = ["powershell", "-NoProfile", "-Command", f"(New-Object -ComObject WScript.Shell).AppActivate('{title}')"]
    elif shutil.which("wmctrl"):
        args = ["wmctrl", "-a", title]
    else:
        return ActionResult(ResultStatus.UNAVAILABLE, "Window focusing is unavailable. Install wmctrl on Linux.")
    if dry_run:
        return ActionResult(ResultStatus.DRY_RUN, f"Would focus window '{title}'.", detail=" ".join(args))
    try:
        completed = subprocess.run(args, capture_output=True, text=True, check=False, timeout=8)
    except (OSError, subprocess.SubprocessError) as exc:
        return ActionResult(ResultStatus.DENIED, f"Could not focus window: {exc}")
    if completed.returncode != 0:
        return ActionResult(ResultStatus.UNAVAILABLE, f"Could not focus window '{title}'.", detail=completed.stderr.strip())
    return ActionResult(ResultStatus.SUCCESS, f"Focused window '{title}'.")
