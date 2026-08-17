from typer.testing import CliRunner

from beton.cli import app


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
