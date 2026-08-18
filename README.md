# BETON

**Your computer, one command away.**

> **Latest release: `v0.3.3`** — [Complete CLI documentation](https://beton-cli.vercel.app/documentation) · [Release notes](https://github.com/itsjustayush/beton-cli/releases/tag/v0.3.3)

BETON is a local-first command layer for everyday computer actions. It provides a short, memorable interface for opening applications and URLs, searching the web, saving notes, starting timers, inspecting the clipboard, checking local capabilities, and controlling selected system actions.

The project is designed to run locally from source. It does not require an account, a server, or cloud storage for its core commands.

## Current status

This repository contains the current published release, version `0.3.3`. It includes the Python CLI, the deployed landing page, the complete command reference, and clean `/documentation` and `/docs` routes. The repository also contains the latest post-release documentation UI refinements. It currently supports:

| Command | Purpose |
|---|---|
| `beton` | Brand screen and quick examples. |
| `beton help` | Example-driven help. |
| `beton open <target>` | Open a URL, site alias, application, file, or folder. |
| `beton search <query>` | Search Google by default, with engine/browser/private-mode options. |
| `beton note <text>` | Save a timestamped local Markdown note. |
| `beton timer <duration>` | Run a foreground countdown. |
| `beton clip` | Read the text clipboard where a platform backend is available. |
| `beton path` | Show Beton’s local data paths. |
| `beton today` | Show notes created today. |
| `beton apps` | List configured application aliases. |
| `beton config` | View and update local settings. |
| `beton doctor` | Inspect runtime and detected capabilities. |
| `beton system <action>` | Dry-run or explicitly invoke lock, sleep, logout, restart, and shutdown actions. |

## Documentation

Read the complete, versioned command reference at [beton-cli.vercel.app/documentation](https://beton-cli.vercel.app/documentation), or use the shorter [beton-cli.vercel.app/docs](https://beton-cli.vercel.app/docs) alias. Release history is available on the [GitHub Releases page](https://github.com/itsjustayush/beton-cli/releases).

## Installation from source

```bash
git clone https://github.com/itsjustayush/beton-cli.git
cd beton-cli
python -m venv .venv
# Activate the virtual environment for your shell.
python -m pip install -e ".[dev]"
beton doctor
```

For a quick local checkout without an editable install:

```bash
PYTHONPATH=src python -m beton --help
```

## Examples

```bash
beton open chrome
beton open https://github.com
beton search "JEE rotation notes"
beton search "private study query" --browser chrome --incognito
beton search "private study query" --browser edge --incognito
beton note "finish physics DPP" --tag study
beton timer 25 --label Physics
beton clip
beton today
beton apps
beton doctor
```

Use `--dry-run` to inspect an external action without performing it:

```bash
beton --dry-run open https://github.com
beton --dry-run search "electrostatics"
beton --dry-run system restart
```

Use `--plain` for terminals where color or decorative output is undesirable:

```bash
beton --plain doctor
```

## Browser behavior

`beton search "query"` uses Google in the operating system’s default browser. The `--browser` option supports explicit browser selection where the executable is available:

```bash
beton search "python typer" --browser chrome
beton search "python typer" --browser edge
beton search "python typer" --browser firefox
```

`--incognito` and private-mode browser flags work only when BETON directly launches the selected browser. It is intentionally rejected with `--browser default` because a generic default-browser handoff cannot guarantee a private window.

## Local data

Beton stores configuration and notes locally. The default data locations are:

| Platform | Default location |
|---|---|
| Linux | `~/.config/beton` |
| macOS | `~/Library/Application Support/Beton` |
| Windows | `%APPDATA%\\Beton` |

Set `BETON_HOME` to use another location, which is useful for testing:

```bash
BETON_HOME=/tmp/beton-test python -m beton note "test note"
```

## Safety model

Beton runs with the permissions of the user who launches it. It does not run permanently as administrator or root. Disruptive system actions require confirmation unless the user explicitly supplies `--yes`; `--dry-run` never performs the action.

The code uses argument-vector subprocess calls rather than concatenating user input into shell strings. The repository should grow through explicit typed commands and platform adapters instead of silently executing arbitrary shell text.

## Development

Run the test suite with:

```bash
pytest
```

Run syntax checks with:

```bash
python -m compileall -q src
```

The architecture is intentionally modular:

```text
CLI input
  → command validation
  → target resolver / service
  → permission policy
  → platform adapter
  → structured ActionResult
  → Rich or plain renderer
```

The next planned additions are reminders, persistent background scheduling, richer file and process operations, media controls, network and hardware commands, richer platform adapters, interactive launcher mode, and standalone binaries. The current `v0.3.3` release focuses on a stable local CLI plus a complete, deployed documentation surface.

## Privacy

Core Beton functionality is local-only. Notes, configuration, and command results are not uploaded. Clipboard contents are never sent remotely or written to logs by the core implementation. Network access occurs only when the user explicitly requests a web action such as `search`.

## License

MIT. See `LICENSE`.
