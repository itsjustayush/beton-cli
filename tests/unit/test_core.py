from datetime import datetime
import shutil
import sys
from pathlib import Path

import pytest

from beton.search import build_search_url
from beton.storage.notes import add_note, today_notes
from beton.timer import format_duration, parse_duration
from beton.platform.base import SubprocessPlatformAdapter


def test_search_url_encodes_query():
    assert build_search_url("JEE rotation notes") == "https://www.google.com/search?q=JEE+rotation+notes"


def test_search_engine_is_explicit():
    assert build_search_url("typer cli", "github") == "https://github.com/search?q=typer+cli"


def test_unknown_search_engine_fails():
    with pytest.raises(Exception):
        build_search_url("query", "unknown")


@pytest.mark.parametrize(
    ("value", "expected"),
    [("25", 1500), ("25m", 1500), ("90s", 90), ("2h", 7200)],
)
def test_parse_duration(value, expected):
    assert parse_duration(value) == expected


def test_format_duration():
    assert format_duration(1500) == "25:00"
    assert format_duration(3661) == "1:01:01"


def test_note_storage_and_today_filter(tmp_path, monkeypatch):
    monkeypatch.setenv("BETON_HOME", str(tmp_path))
    path = add_note("finish physics DPP", "study")
    assert path.exists()
    assert "finish physics DPP" in path.read_text(encoding="utf-8")
    assert len(today_notes()) == 1


def test_windows_chrome_path_resolution(tmp_path, monkeypatch):
    chrome = tmp_path / "Google" / "Chrome" / "Application" / "chrome.exe"
    chrome.parent.mkdir(parents=True)
    chrome.write_text("placeholder", encoding="utf-8")
    monkeypatch.setattr(sys, "platform", "win32")
    monkeypatch.setattr(shutil, "which", lambda target: None)
    monkeypatch.setenv("PROGRAMFILES", str(tmp_path))
    monkeypatch.setenv("PROGRAMFILES(X86)", "")
    monkeypatch.setenv("LOCALAPPDATA", "")
    monkeypatch.setenv("APPDATA", "")

    adapter = SubprocessPlatformAdapter()
    assert adapter._application_executable("chrome") == str(chrome)
