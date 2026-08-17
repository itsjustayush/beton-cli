"""Platform adapter selection."""

from __future__ import annotations

import platform

from .base import PlatformAdapter, SubprocessPlatformAdapter


class WindowsAdapter(SubprocessPlatformAdapter):
    pass


class MacOSAdapter(SubprocessPlatformAdapter):
    pass


class LinuxAdapter(SubprocessPlatformAdapter):
    pass


def get_adapter() -> PlatformAdapter:
    system = platform.system()
    if system == "Windows":
        return WindowsAdapter()
    if system == "Darwin":
        return MacOSAdapter()
    return LinuxAdapter()


__all__ = ["PlatformAdapter", "get_adapter"]
