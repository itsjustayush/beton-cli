"""Safe self-upgrade support for official BETON source checkouts."""

from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from .errors import BetonError

OFFICIAL_REMOTE = "https://github.com/itsjustayush/beton-cli"
DEFAULT_BRANCH = "main"


@dataclass(frozen=True)
class UpgradeResult:
    """Outcome of a source-checkout upgrade attempt."""

    root: Path
    before: str
    after: str
    changed: bool
    dry_run: bool = False


def _normalise_remote(value: str) -> str:
    value = value.strip()
    if value.startswith("git@github.com:"):
        value = "https://github.com/" + value.removeprefix("git@github.com:")
    if value.endswith(".git"):
        value = value[:-4]
    return value.rstrip("/")


def _git(root: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError as exc:
        raise BetonError(f"Git is required for upgrades but could not be started: {exc}") from exc
    if check and result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        raise BetonError(f"Git command failed: git {' '.join(args)}\n{detail}")
    return result


def repository_root() -> Path:
    """Find the source checkout containing the installed Beton package."""

    package_file = Path(__file__).resolve()
    for candidate in (package_file.parent, *package_file.parents):
        if (candidate / ".git").exists():
            return candidate
    raise BetonError(
        "Automatic upgrades require an official Beton source checkout. "
        "Clone https://github.com/itsjustayush/beton-cli and run Beton from that environment."
    )


def _assert_official_checkout(root: Path) -> str:
    remote = _git(root, "remote", "get-url", "origin").stdout.strip()
    if _normalise_remote(remote) != OFFICIAL_REMOTE:
        raise BetonError(
            "Automatic upgrades are limited to the official repository "
            f"({OFFICIAL_REMOTE}). Current origin: {remote or 'not configured'}"
        )
    branch = _git(root, "branch", "--show-current").stdout.strip()
    if branch not in {DEFAULT_BRANCH, ""}:
        raise BetonError(
            f"Automatic upgrades must run on the {DEFAULT_BRANCH!r} branch or an official "
            f"release checkout; current branch is {branch!r}."
        )
    return branch


def _assert_clean(root: Path) -> None:
    status = _git(root, "status", "--porcelain").stdout.strip()
    if status:
        raise BetonError(
            "Upgrade stopped because the source checkout has uncommitted changes. "
            "Commit, stash, or discard them before running `beton version --upgrade`."
        )


def _install_current_checkout(root: Path) -> None:
    command = [sys.executable, "-m", "pip", "install", "--no-deps", "-e", "."]
    try:
        result = subprocess.run(command, cwd=root, check=False, capture_output=True, text=True)
    except OSError as exc:
        raise BetonError(f"The updated source was fetched, but pip could not be started: {exc}") from exc
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        raise BetonError(
            "The source was updated, but the current Python environment could not be refreshed. "
            f"Run `{' '.join(command)}` manually.\n{detail}"
        )


def upgrade(*, dry_run: bool = False) -> UpgradeResult:
    """Fast-forward the official source checkout and refresh the active environment."""

    root = repository_root()
    branch = _assert_official_checkout(root)
    _assert_clean(root)
    before = _git(root, "rev-parse", "HEAD").stdout.strip()

    if dry_run:
        return UpgradeResult(root=root, before=before, after=before, changed=False, dry_run=True)

    if branch:
        _git(root, "pull", "--ff-only", "origin", DEFAULT_BRANCH)
    else:
        remote_ref = f"refs/remotes/origin/{DEFAULT_BRANCH}"
        _git(root, "fetch", "origin", f"{DEFAULT_BRANCH}:{remote_ref}", "--depth=1")
        _git(root, "checkout", "-B", DEFAULT_BRANCH, remote_ref)
    after = _git(root, "rev-parse", "HEAD").stdout.strip()
    if after != before:
        try:
            _install_current_checkout(root)
        except BetonError:
            _git(root, "reset", "--hard", before, check=False)
            raise
    return UpgradeResult(root=root, before=before, after=after, changed=after != before)
