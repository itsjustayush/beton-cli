# Changelog

## 0.1.0 — Initial foundation

- Added Typer-based CLI and Rich/plain rendering.
- Added `open`, `search`, `note`, `timer`, `clip`, `path`, `today`, `apps`, `config`, and `doctor`.
- Added deterministic URL and target resolution.
- Added browser selection and explicit private-mode handling.
- Added local Markdown notes and configurable local data directory.
- Added dry-run support for external actions.
- Added platform adapter foundation for Windows, macOS, and Linux.
- Added bounded file search and read-only process inspection.
- Added guarded system lock, sleep, logout, restart, and shutdown commands.
- Added unit and CLI integration tests.

## 0.2.0 — Local machine-control expansion

The second release adds local reminders and tasks, file copy/move/rename/trash operations, guarded process termination, screenshot capture adapters, active-window inspection and focus helpers, volume/media/battery/network commands, Git status shortcuts, plugin registry management, clipboard write/clear/history commands, weather lookup, and opt-in AI commands for ask, explain, rewrite, summarize, and translate.

The new integrations remain capability-aware. Unsupported operating-system features return clear unavailable results, destructive actions require confirmation, and `--dry-run` previews external actions without executing them.
