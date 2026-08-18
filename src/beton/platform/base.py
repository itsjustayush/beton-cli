"""Platform abstraction interfaces and common target resolution helpers."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import webbrowser
from abc import ABC, abstractmethod
from pathlib import Path
from urllib.parse import urlparse

from ..models import ActionResult, Capability, ResultStatus


class PlatformAdapter(ABC):
    """Operations Beton may delegate to the host operating system."""

    @abstractmethod
    def open_url(self, url: str, browser: str = "default", incognito: bool = False, dry_run: bool = False) -> ActionResult:
        raise NotImplementedError

    @abstractmethod
    def open_path(self, path: Path, dry_run: bool = False) -> ActionResult:
        raise NotImplementedError

    @abstractmethod
    def launch_app(self, target: str, dry_run: bool = False) -> ActionResult:
        raise NotImplementedError

    @abstractmethod
    def capabilities(self) -> list[Capability]:
        raise NotImplementedError

    def can_run(self, executable: str) -> bool:
        return shutil.which(executable) is not None


class SubprocessPlatformAdapter(PlatformAdapter):
    """Shared adapter behavior using safe argument-vector subprocess calls."""

    browser_candidates = {
        "chrome": ["google-chrome", "google-chrome-stable", "chrome", "chrome.exe"],
        "edge": ["microsoft-edge", "msedge", "msedge.exe"],
        "firefox": ["firefox", "firefox.exe"],
    }

    def _browser_executable(self, browser: str) -> str | None:
        candidates = self.browser_candidates.get(browser, [])
        return next((candidate for candidate in candidates if shutil.which(candidate)), None)

    def open_url(self, url: str, browser: str = "default", incognito: bool = False, dry_run: bool = False) -> ActionResult:
        if browser == "default":
            if incognito:
                return ActionResult(
                    ResultStatus.UNAVAILABLE,
                    "Incognito mode requires an explicit browser: chrome, edge, or firefox.",
                )
            if dry_run:
                return ActionResult(ResultStatus.DRY_RUN, f"Would open {url} in the default browser.")
            opened = webbrowser.open_new_tab(url)
            if not opened:
                return ActionResult(ResultStatus.UNAVAILABLE, "Could not open the default browser.")
            return ActionResult(ResultStatus.SUCCESS, f"Opened {url} in the default browser.")

        if browser not in self.browser_candidates:
            return ActionResult(ResultStatus.UNAVAILABLE, f"Unsupported browser '{browser}'.")
        executable = self._browser_executable(browser)
        if not executable:
            return ActionResult(ResultStatus.UNAVAILABLE, f"Could not find {browser} on PATH.")

        args = [executable]
        if incognito:
            args.append("--incognito" if browser == "chrome" else "--inprivate" if browser == "edge" else "--private-window")
        args.append(url)
        if dry_run:
            return ActionResult(ResultStatus.DRY_RUN, "Would launch browser.", detail=" ".join(args))
        try:
            subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except OSError as exc:
            return ActionResult(ResultStatus.DENIED, f"Could not launch {browser}: {exc}")
        mode = " in private mode" if incognito else ""
        return ActionResult(ResultStatus.SUCCESS, f"Opened {url} in {browser}{mode}.")

    def open_path(self, path: Path, dry_run: bool = False) -> ActionResult:
        if not path.exists():
            return ActionResult(ResultStatus.UNAVAILABLE, f"Path does not exist: {path}")
        if dry_run:
            return ActionResult(ResultStatus.DRY_RUN, f"Would open {path}.")
        try:
            if sys.platform.startswith("win"):
                os_startfile = getattr(__import__("os"), "startfile")
                os_startfile(str(path))
            elif sys.platform == "darwin":
                subprocess.Popen(["open", str(path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                subprocess.Popen(["xdg-open", str(path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except (OSError, AttributeError) as exc:
            return ActionResult(ResultStatus.UNAVAILABLE, f"Could not open {path}: {exc}")
        return ActionResult(ResultStatus.SUCCESS, f"Opened {path}.")

    def launch_app(self, target: str, dry_run: bool = False) -> ActionResult:
        executable = self._application_executable(target)
        if executable:
            if dry_run:
                return ActionResult(ResultStatus.DRY_RUN, f"Would launch {target}.", detail=executable)
            try:
                subprocess.Popen([executable], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except OSError as exc:
                return ActionResult(ResultStatus.DENIED, f"Could not launch {target}: {exc}")
            return ActionResult(ResultStatus.SUCCESS, f"Opened {target}.")
        return ActionResult(
            ResultStatus.UNAVAILABLE,
            f"Could not find application '{target}'. Install it or pass its executable path.",
        )

    def _application_executable(self, target: str) -> str | None:
        executable = shutil.which(target)
        if executable:
            return executable
        if not sys.platform.startswith("win"):
            return None

        roots = [
            Path(os.environ.get("PROGRAMFILES", "")),
            Path(os.environ.get("PROGRAMFILES(X86)", "")),
            Path(os.environ.get("LOCALAPPDATA", "")),
            Path(os.environ.get("APPDATA", "")),
        ]
        known_paths = {
            "chrome": [
                Path("Google/Chrome/Application/chrome.exe"),
            ],
            "code": [
                Path("Microsoft VS Code/Code.exe"),
                Path("Programs/Microsoft VS Code/Code.exe"),
            ],
            "spotify": [
                Path("Spotify/Spotify.exe"),
            ],
        }
        for relative in known_paths.get(target.lower(), []):
            for root in roots:
                candidate = root / relative
                if candidate.is_file():
                    return str(candidate)
        return None

    def capabilities(self) -> list[Capability]:
        return [
            Capability("url.open", True, "Python webbrowser and named browser launchers"),
            Capability("path.open", True, "Native file-manager association"),
            Capability("app.launch", True, "PATH-based executable launch"),
        ]


def is_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)
