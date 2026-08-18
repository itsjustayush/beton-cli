import subprocess

import pytest
from typer.testing import CliRunner

import beton.upgrade as upgrade_module
from beton.cli import app
from beton.upgrade import UpgradeResult


runner = CliRunner()


def test_help_command():
    result = runner.invoke(app, ["--plain", "help"])
    assert result.exit_code == 0
    assert "BETON" in result.stdout
    assert "search" in result.stdout


def test_search_dry_run():
    result = runner.invoke(app, ["--dry-run", "search", "electrostatics"])
    assert result.exit_code == 0
    assert "Would open" in result.stdout
    assert "electrostatics" in result.stdout


def test_note_writes_to_local_home(tmp_path, monkeypatch):
    monkeypatch.setenv("BETON_HOME", str(tmp_path))
    result = runner.invoke(app, ["note", "finish physics DPP"])
    assert result.exit_code == 0
    assert "Saved note locally" in result.stdout
    assert "finish physics DPP" in (tmp_path / "notes.md").read_text(encoding="utf-8")


def test_system_dry_run_does_not_execute():
    result = runner.invoke(app, ["--dry-run", "system", "restart"])
    assert result.exit_code == 0
    assert "Would perform system action: restart" in result.stdout


def test_search_private_default_browser_is_rejected():
    result = runner.invoke(app, ["search", "private query", "--incognito"])
    assert result.exit_code != 0
    assert "explicit browser" in result.stdout.lower()


def test_version_command_preserves_version_output():
    result = runner.invoke(app, ["--plain", "version"])
    assert result.exit_code == 0
    assert result.stdout.strip() == "BETON 0.4.3"


def test_version_upgrade_dry_run(monkeypatch, tmp_path):
    preview = UpgradeResult(
        root=tmp_path,
        before="0123456789abcdef",
        after="0123456789abcdef",
        changed=False,
        dry_run=True,
    )
    monkeypatch.setattr("beton.cli.upgrade_checkout", lambda dry_run: preview)
    result = runner.invoke(app, ["--plain", "--dry-run", "version", "--upgrade"])
    assert result.exit_code == 0
    assert "Would check GitHub and update" in result.stdout
    assert "01234567" in result.stdout


def test_detached_upgrade_fetches_remote_tracking_branch(monkeypatch, tmp_path):
    calls = []
    revisions = iter(["before", "after"])

    def fake_git(root, *args, check=True):
        calls.append(args)
        if args[:3] == ("remote", "get-url", "origin"):
            stdout = "https://github.com/itsjustayush/beton-cli.git\n"
        elif args[:2] == ("branch", "--show-current"):
            stdout = ""
        elif args[:2] == ("rev-parse", "HEAD"):
            stdout = f"{next(revisions)}\n"
        else:
            stdout = ""
        return subprocess.CompletedProcess(["git", *args], 0, stdout=stdout, stderr="")

    monkeypatch.setattr(upgrade_module, "repository_root", lambda: tmp_path)
    monkeypatch.setattr(upgrade_module, "_git", fake_git)
    monkeypatch.setattr(upgrade_module, "_assert_clean", lambda root: None)
    monkeypatch.setattr(upgrade_module, "_install_current_checkout", lambda root: None)

    result = upgrade_module.upgrade()

    assert result.changed is True
    assert ("fetch", "origin", "main:refs/remotes/origin/main", "--depth=1") in calls
    assert ("checkout", "-B", "main", "refs/remotes/origin/main") in calls
