# Contributing to BETON

Thank you for helping improve BETON. The project is a local-first command layer for everyday computer actions, so contributions should preserve predictable command language, explicit side effects, platform-aware behavior, and readable implementation boundaries.

## Before you start

Read the [README](README.md), [security policy](SECURITY.md), and [Code of Conduct](CODE_OF_CONDUCT.md). For the current user-facing command reference, visit the [deployed documentation](https://beton-cli.vercel.app/documentation). Do not include secrets, credentials, private local paths, or clipboard contents in issues, pull requests, tests, screenshots, or logs.

## Set up a development checkout

Beton is developed from the official GitHub repository rather than installed from PyPI. Clone the current release or the `main` branch, create a virtual environment, and install the project with development dependencies:

```bash
git clone https://github.com/itsjustayush/beton-cli.git
cd beton-cli
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

Windows PowerShell users can use:

```powershell
git clone https://github.com/itsjustayush/beton-cli.git
Set-Location beton-cli
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

## Validate changes

Run the test suite and syntax checks before opening a pull request:

```bash
pytest
python -m compileall -q src
```

When a change affects a command, also run its help output and a safe dry-run where available. Do not launch real applications, modify real system state, send network requests, or invoke disruptive system actions as part of automated tests.

## Implementation principles

New commands should use typed arguments and options, a clear service or platform-adapter boundary, structured `ActionResult` values where applicable, and documentation with realistic examples. External actions should expose a dry-run path. Disruptive actions must retain explicit confirmation behavior and should be reviewed for Linux, macOS, and Windows differences.

Avoid adding network dependencies to the core. Do not concatenate user input into shell strings or execute arbitrary shell text. Keep local data handling explicit, and preserve the `--plain`, `--dry-run`, `--verbose`, `--version`, and `--help` behavior when modifying the CLI callback or renderers.

## Documentation and website changes

Update the README, changelog, and deployed documentation when user-facing behavior changes. Keep examples aligned with the commands implemented in `src/beton/cli.py`; do not document roadmap ideas as if they were available. Website changes live under `website/` and should pass the production build:

```bash
npm --prefix website run build
```

## Issues and pull requests

Use the repository issue forms for bug reports and feature proposals. Security vulnerabilities must be reported privately according to `SECURITY.md`. A pull request should explain the problem, implementation, validation performed, documentation impact, and any safety or privacy considerations. Keep each change focused and reviewable.

## Release conventions

User-facing version changes follow Semantic Versioning. Release notes should describe the actual historical change, installation path, compatibility considerations, and validation status. Tags and releases are created by maintainers after the main branch is synchronized.
