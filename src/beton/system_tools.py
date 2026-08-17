"""Best-effort platform command adapters for common system utilities."""

from __future__ import annotations

import platform
import shutil
import subprocess

from .models import ActionResult, ResultStatus


def _run(args: list[str], message: str, dry_run: bool = False) -> ActionResult:
    if dry_run:
        return ActionResult(ResultStatus.DRY_RUN, message, detail=" ".join(args))
    try:
        completed = subprocess.run(args, capture_output=True, text=True, timeout=8)
    except (OSError, subprocess.SubprocessError) as exc:
        return ActionResult(ResultStatus.UNAVAILABLE, f"Could not run system command: {exc}")
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip()
        return ActionResult(ResultStatus.DENIED, f"System command failed: {message}", detail=detail)
    return ActionResult(ResultStatus.SUCCESS, message, detail=completed.stdout.strip() or None)


def volume(value: str, dry_run: bool = False) -> ActionResult:
    system = platform.system()
    if value.lower() == "mute":
        if system == "Darwin":
            return _run(["osascript", "-e", "set volume output muted true"], "Muted volume.", dry_run)
        if shutil.which("pactl"):
            return _run(["pactl", "set-sink-mute", "@DEFAULT_SINK@", "toggle"], "Toggled volume mute.", dry_run)
    if system == "Darwin":
        return _run(["osascript", "-e", f"set volume output volume {value}"], f"Set volume to {value}.", dry_run)
    if shutil.which("pactl"):
        return _run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"{value}%"], f"Set volume to {value}%.", dry_run)
    if system == "Windows":
        return ActionResult(ResultStatus.UNAVAILABLE, "Windows volume control needs a native audio adapter in this version.")
    return ActionResult(ResultStatus.UNAVAILABLE, "No supported volume utility was detected.")


def media(action: str, dry_run: bool = False) -> ActionResult:
    if dry_run:
        return ActionResult(ResultStatus.DRY_RUN, f"Would request media action: {action}.")
    if shutil.which("playerctl"):
        return _run(["playerctl", action], f"Requested media action: {action}.", dry_run)
    if platform.system() == "Darwin":
        script = {"play": "play", "pause": "pause", "next": "next track", "previous": "previous track"}.get(action)
        if script:
            return _run(["osascript", "-e", f'tell application "Music" to {script}'], f"Requested media action: {action}.", dry_run)
    return ActionResult(ResultStatus.UNAVAILABLE, "No supported media controller was detected. Install playerctl on Linux.")


def battery(dry_run: bool = False) -> ActionResult:
    if dry_run:
        return ActionResult(ResultStatus.DRY_RUN, "Would read battery status.")
    if platform.system() == "Darwin":
        return _run(["pmset", "-g", "batt"], "Read battery status.", dry_run)
    if shutil.which("upower"):
        return _run(["upower", "-i", "/org/freedesktop/UPower/devices/battery_BAT0"], "Read battery status.", dry_run)
    if platform.system() == "Windows":
        return _run(["powershell", "-NoProfile", "-Command", "Get-CimInstance Win32_Battery | Format-List"], "Read battery status.", dry_run)
    return ActionResult(ResultStatus.UNAVAILABLE, "Battery status is unavailable on this system.")


def network_info(kind: str, target: str | None = None, dry_run: bool = False) -> ActionResult:
    system = platform.system()
    if dry_run:
        target_text = f" for {target}" if target else ""
        return ActionResult(ResultStatus.DRY_RUN, f"Would inspect {kind}{target_text}.")
    if kind == "ip":
        args = ["ipconfig"] if system == "Windows" else ["ifconfig"] if system == "Darwin" else ["ip", "addr"]
        if shutil.which(args[0]):
            return _run(args, "Read network interface information.", dry_run)
    if kind == "wifi":
        if system == "Windows":
            return _run(["netsh", "wlan", "show", "interfaces"], "Read Wi-Fi status.", dry_run)
        if system == "Darwin":
            return _run(["networksetup", "-getinfo", "Wi-Fi"], "Read Wi-Fi status.", dry_run)
        if shutil.which("nmcli"):
            return _run(["nmcli", "radio", "wifi"], "Read Wi-Fi status.", dry_run)
    if kind == "ping" and target:
        return _run(["ping", "-n" if system == "Windows" else "-c", "1", target], f"Pinged {target}.", dry_run)
    if kind == "dns" and target:
        executable = "nslookup" if shutil.which("nslookup") else "dig" if shutil.which("dig") else None
        if executable:
            return _run([executable, target], f"Looked up DNS for {target}.", dry_run)
    return ActionResult(ResultStatus.UNAVAILABLE, f"Network capability '{kind}' is unavailable on this system.")
