"""Platform-aware system and session controls."""

from __future__ import annotations

import platform
import subprocess
from typing import Sequence

from .models import ActionResult, ResultStatus


_ACTIONS: dict[str, dict[str, Sequence[str]]] = {
    "Windows": {
        "lock": ["rundll32.exe", "user32.dll,LockWorkStation"],
        "sleep": ["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"],
        "logout": ["shutdown.exe", "/l"],
        "restart": ["shutdown.exe", "/r", "/t", "0"],
        "shutdown": ["shutdown.exe", "/s", "/t", "0"],
    },
    "Darwin": {
        "lock": ["/System/Library/CoreServices/Menu Extras/User.menu/Contents/Resources/CGSession", "-suspend"],
        "sleep": ["pmset", "sleepnow"],
        "logout": ["osascript", "-e", 'tell application "System Events" to log out'],
        "restart": ["osascript", "-e", 'tell application "System Events" to restart'],
        "shutdown": ["osascript", "-e", 'tell application "System Events" to shut down'],
    },
    "Linux": {
        "lock": ["loginctl", "lock-session"],
        "sleep": ["systemctl", "suspend"],
        "logout": ["loginctl", "terminate-user"],
        "restart": ["systemctl", "reboot"],
        "shutdown": ["systemctl", "poweroff"],
    },
}


def system_action(action: str, *, dry_run: bool = False) -> ActionResult:
    system = platform.system()
    commands = _ACTIONS.get(system, _ACTIONS["Linux"])
    args = list(commands.get(action, []))
    if not args:
        return ActionResult(ResultStatus.UNAVAILABLE, f"System action '{action}' is unsupported on {system}.")
    if dry_run:
        return ActionResult(ResultStatus.DRY_RUN, f"Would perform system action: {action}.", detail=" ".join(args))
    try:
        subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except OSError as exc:
        return ActionResult(ResultStatus.DENIED, f"Could not perform {action}: {exc}")
    return ActionResult(ResultStatus.SUCCESS, f"Requested system action: {action}.")
