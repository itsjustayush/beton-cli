from pathlib import Path

from beton.files import copy_path, move_path, rename_path, trash_path
from beton.models import ResultStatus
from beton.storage.reminders import add_reminder, complete_reminder, list_reminders, parse_due
from beton.system_tools import battery, media, network_info


def test_reminder_lifecycle(tmp_path, monkeypatch):
    monkeypatch.setenv("BETON_HOME", str(tmp_path))
    item = add_reminder("test reminder", parse_due("30m"))
    assert item["text"] == "test reminder"
    assert list_reminders()[0]["id"] == item["id"]
    assert complete_reminder(str(item["id"]))["done"] is True
    assert list_reminders() == []


def test_file_operations(tmp_path):
    source = tmp_path / "source.txt"
    source.write_text("hello", encoding="utf-8")
    copied = tmp_path / "copied.txt"
    moved = tmp_path / "moved.txt"
    assert copy_path(source, copied).status == ResultStatus.SUCCESS
    assert move_path(copied, moved).status == ResultStatus.SUCCESS
    assert rename_path(moved, "renamed.txt").status == ResultStatus.SUCCESS
    assert (tmp_path / "renamed.txt").exists()


def test_file_dry_run_does_not_change_files(tmp_path):
    source = tmp_path / "source.txt"
    source.write_text("hello", encoding="utf-8")
    result = trash_path(source, dry_run=True)
    assert result.status == ResultStatus.DRY_RUN
    assert source.exists()


def test_system_tools_have_dry_run_results():
    assert media("pause", dry_run=True).status == ResultStatus.DRY_RUN
    assert battery(dry_run=True).status == ResultStatus.DRY_RUN
    assert network_info("ping", "example.com", dry_run=True).status == ResultStatus.DRY_RUN
