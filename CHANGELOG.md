# Changelog

## 0.5.0 — npm distribution channel

- Added the official `beton-cli` npm wrapper for `npm install -g beton-cli`.
- Added cross-platform bootstrap logic that downloads the matching GitHub release, creates an isolated Python virtual environment, and exposes the `beton` command without requiring Git or PowerShell activation.
- Added npm-aware `beton version --upgrade` behavior for globally installed instances.
- Added package-specific README and MIT license files.
- Made npm the recommended installation path while retaining the official GitHub source workflow for contributors.
- Updated version metadata, examples, landing-page labels, and deployed documentation to v0.5.0.

All notable Beton CLI releases are documented here. The project follows Semantic Versioning while it remains below `1.0.0`.

## 0.4.3 — Reliable tag-checkout upgrades

- Fixed `beton version --upgrade` for users installed from a detached release tag.
- Explicitly fetches `main` into `refs/remotes/origin/main` before switching branches, so a prior `git fetch --tags origin` is sufficient.
- Added regression coverage for the detached-checkout remote-tracking branch flow.
- Published as the current [GitHub release v0.4.3](https://github.com/itsjustayush/beton-cli/releases/tag/v0.4.3).

## 0.4.2 — Simplified Windows workflow

- Added a one-command `scripts/install.ps1` setup path that works without activating `Activate.ps1`.
- Added a user-level `%USERPROFILE%\\bin\\beton.cmd` shim so a new terminal can run `beton` without a long `.venv\\Scripts\\beton.exe` path.
- Added `--NoPath` to the installer for users who prefer direct virtual-environment executables.
- Improved Windows resolution for common `chrome`, `code`, and `spotify` installations.
- Added clearer `beton help` guidance explaining that `beton` alone shows the brand screen and `beton beton` is invalid.
- Added tests for Windows Chrome path resolution.
- Published as the current [GitHub release v0.4.2](https://github.com/itsjustayush/beton-cli/releases/tag/v0.4.2).

## 0.4.1 — Windows-safe source installation

- Removed mandatory PowerShell activation from the Windows installation path.
- Added direct `.venv\\Scripts\\python.exe` and `.venv\\Scripts\\beton.exe` commands that work without changing PowerShell execution policy.
- Added explicit Python installation and PATH guidance for Windows, including the `py` and `python` command failure case.
- Clarified that the annotated-tag warning from a shallow `git clone` is nonfatal when Git exits successfully and switches to a commit.
- Added direct Windows executable examples for `beton version --upgrade`, `--yes`, and `--dry-run`.
- Published as the current [GitHub release v0.4.1](https://github.com/itsjustayush/beton-cli/releases/tag/v0.4.1).

## 0.4.0 — Safe source-checkout upgrades

- Added `beton version` as a read-only subcommand that reports the installed version.
- Added `beton version --upgrade` to fast-forward an official `itsjustayush/beton-cli` checkout from `origin/main` and refresh the active Python environment without a manual reinstall.
- Added confirmation by default, `--yes` for explicit non-interactive confirmation, and `--dry-run` preview support.
- Refused upgrades on non-official remotes, non-`main` branches, dirty working trees, or non-fast-forward histories.
- Added rollback to the previous commit if refreshing the active environment fails.
- Documented the workflow in the README and deployed command reference.
- Published as the current [GitHub release v0.4.0](https://github.com/itsjustayush/beton-cli/releases/tag/v0.4.0).

## 0.3.4 — Corrected source installation and documentation

- Corrected the README and deployed documentation to state that Beton is not currently distributed as a PyPI package.
- Added official GitHub source installation instructions pinned to the `v0.3.4` tag for Linux/macOS and Windows PowerShell.
- Clarified that pip is used only to install the cloned local source tree, not to download Beton from PyPI.
- Synchronized package metadata, runtime version output, landing-page release labels, documentation examples, and project URLs.
- Refined the documentation UI with clearer code panels, separate PowerShell examples, calmer emphasis, and accessible motion behavior.
- Published as the current [GitHub release v0.3.4](https://github.com/itsjustayush/beton-cli/releases/tag/v0.3.4).

## 0.3.3 — Documentation route alias

- Added the short `/docs` alias for the canonical `/documentation` route.
- Included the alias in the Vite multi-page build and preserved `/documentation` as the canonical URL.
- Published as [GitHub release v0.3.3](https://github.com/itsjustayush/beton-cli/releases/tag/v0.3.3).

## 0.3.2 — Canonical documentation route

- Replaced the space-containing documentation filename with `documentation.html`.
- Updated landing-page links and Vercel routing for `/documentation`.
- Published as [GitHub release v0.3.2](https://github.com/itsjustayush/beton-cli/releases/tag/v0.3.2).

## 0.3.1 — Documentation navigation

- Linked the landing page and documentation page in both directions.
- Added documentation links to the landing navigation, hero, implementation section, and footer.
- Published as [GitHub release v0.3.1](https://github.com/itsjustayush/beton-cli/releases/tag/v0.3.1).

## 0.3.0 — Complete CLI documentation

- Added the comprehensive Beton CLI documentation page.
- Documented installation, quickstart, every command, flags, configuration, aliases, data storage, browser control, dry run, plain mode, and troubleshooting.
- Added responsive navigation, search, copyable code blocks, theme switching, cards, tables, and safety callouts.
- Published as [GitHub release v0.3.0](https://github.com/itsjustayush/beton-cli/releases/tag/v0.3.0).

## 0.2.2 — Brand asset and loading polish

- Added the Beton favicon.
- Added lazy loading for the landing-page portrait.
- Published as [GitHub release v0.2.2](https://github.com/itsjustayush/beton-cli/releases/tag/v0.2.2).

## 0.2.1 — Deployment and presentation refinement

- Corrected the Vercel frontend build context.
- Improved landing-page motion and developer-profile presentation.
- Published as [GitHub release v0.2.1](https://github.com/itsjustayush/beton-cli/releases/tag/v0.2.1).

## 0.2.0 — Vercel landing page

- Added the Vite-based static landing page.
- Added Vercel deployment configuration and the isolated website build.
- Published as [GitHub release v0.2.0](https://github.com/itsjustayush/beton-cli/releases/tag/v0.2.0).

## 0.1.1 — Foundation stabilization

- Reverted the experimental local-machine command expansion before it became part of the supported release surface.
- Restored the focused CLI architecture and documentation model from the foundation release.
- Published as [GitHub release v0.1.1](https://github.com/itsjustayush/beton-cli/releases/tag/v0.1.1).

## 0.1.0 — Functional CLI foundation

- Added the Typer-based CLI and Rich/plain rendering.
- Added `open`, `search`, `note`, `timer`, `clip`, `path`, `today`, `apps`, `config`, and `doctor`.
- Added deterministic URL and target resolution, browser selection, private-mode handling, local Markdown notes, configurable data directories, and dry-run support.
- Added platform adapters, bounded file search, read-only process inspection, guarded system actions, tests, installation scripts, and project policy documents.
- Published as [GitHub release v0.1.0](https://github.com/itsjustayush/beton-cli/releases/tag/v0.1.0).

## 0.0.1 — Repository initialization

- Established the initial Beton CLI repository and project README.
- Published as [GitHub release v0.0.1](https://github.com/itsjustayush/beton-cli/releases/tag/v0.0.1).
