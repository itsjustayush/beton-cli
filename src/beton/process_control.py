"""Guarded process termination helpers."""

from __future__ import annotations

import os
import platform
import signal
import subprocess

from .models import ActionResult, ResultStatus


def terminate_process(target: str, force: bool = False, dry_run: bool = False) -> ActionResult:
    if target.isdigit():
        pid = int(target)
        if platform.system() == "Windows":
            args = ["taskkill", "/PID", str(pid), "/F" if force else "/T"]
            if dry_run:
                return ActionResult(ResultStatus.DRY_RUN, f"Would terminate process {pid}.", detail=" ".join(args))
            try:
                completed = subprocess.run(args, capture_output=True, text=True, check=False, timeout=8)
            except (OSError, subprocess.SubprocessError) as exc:
                return ActionResult(ResultStatus.UNAVAILABLE, f"Could not terminate process: {exc}")
            return ActionResult(ResultStatus.SUCCESS if completed.returncode == 0 else ResultStatus.DENIED, f"Terminated process {pid}.", detail=completed.stderr.strip() or completed.stdout.strip())
        if dry_run:
            return ActionResult(ResultStatus.DRY_RUN, f"Would send {'SIGKILL' if force else 'SIGTERM'} to process {pid}.")
        try:
            os.kill(pid, signal.SIGKILL if force else signal.SIGTERM)
        except OSError as exc:
            return ActionResult(ResultStatus.DENIED, f"Could not terminate process {pid}: {exc}")
        return ActionResult(ResultStatus.SUCCESS, f"Terminated process {pid}.")

    if platform.system() == "Windows":
        args = ["taskkill", "/IM", target, "/F" if force else "/T"]
    else:
        args = ["pkill", "-KILL" if force else "-TERM", "-f", target]
    if dry_run:
        return ActionResult(ResultStatus.DRY_RUN, f"Would terminate processes matching {target}.", detail=" ".join(args))
    try:
        completed = subprocess.run(args, capture_output=True, text=True, check=False, timeout=8)
    except (OSError, subprocess.SubprocessError) as exc:
        return ActionResult(ResultStatus.UNAVAILABLE, f"Could not terminate process: {exc}")
    if completed.returncode != 0:
        return ActionResult(ResultStatus.UNAVAILABLE, f"No process matched {target}.", detail=completed.stderr.strip())
    return ActionResult(ResultStatus.SUCCESS, f"Terminated processes matching {target}.")
