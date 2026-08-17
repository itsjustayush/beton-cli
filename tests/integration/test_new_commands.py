from typer.testing import CliRunner

from beton.cli import app


runner = CliRunner()


def test_reminder_command(tmp_path, monkeypatch):
    monkeypatch.setenv("BETON_HOME", str(tmp_path))
    result = runner.invoke(app, ["remind", "add", "study", "--in", "30m"])
    assert result.exit_code == 0
    assert "Created reminder" in result.stdout
    listed = runner.invoke(app, ["remind", "list"])
    assert listed.exit_code == 0
    assert "study" in listed.stdout


def test_file_dry_run(tmp_path):
    result = runner.invoke(app, ["--dry-run", "file", "copy", str(tmp_path / "a"), str(tmp_path / "b")])
    assert result.exit_code == 0
    assert "Would copy" in result.stdout


def test_plugin_registry(tmp_path, monkeypatch):
    monkeypatch.setenv("BETON_HOME", str(tmp_path))
    result = runner.invoke(app, ["plugin", "enable", "weather"])
    assert result.exit_code == 0
    listed = runner.invoke(app, ["plugin", "list"])
    assert listed.exit_code == 0
    assert "weather" in listed.stdout


def test_process_kill_dry_run():
    result = runner.invoke(app, ["--dry-run", "kill", "1234"])
    assert result.exit_code == 0
    assert "Would send" in result.stdout


def test_ai_command_requires_opt_in(monkeypatch):
    monkeypatch.delenv("BETON_AI_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    result = runner.invoke(app, ["ask", "hello"])
    assert result.exit_code != 0
    assert "AI is disabled" in (result.stdout + result.stderr)
