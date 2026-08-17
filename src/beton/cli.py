"""BETON command-line entry point."""

from __future__ import annotations

import platform
import shutil
import subprocess
import time
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from . import __version__
from .config import config_path, data_dir, load_config, notes_path, save_config, set_config_value
from .errors import BetonError, ConfigurationError
from .models import ActionResult, ResultStatus
from .machine import find_files, process_rows
from .files import copy_path, move_path, rename_path, trash_path
from .process_control import terminate_process
from .screenshot import capture
from .window_control import active_window, focus_window
from .plugins import list_plugins, set_plugin
from .ai import complete
from .clipboard import clear_clipboard, clipboard_history, read_clipboard, write_clipboard
from .tasks import add_task, cancel_task, complete_task, list_tasks
from .weather import weather
from .storage.reminders import add_reminder, cancel_reminder, complete_reminder, list_reminders, parse_due
from .system_tools import battery, media, network_info, volume
from .output import render_brand, render_result, render_table
from .platform import get_adapter
from .resolver import resolve_target
from .search import SEARCH_URLS, build_search_url
from .storage.notes import add_note, today_notes
from .timer import format_duration, parse_duration
from .system import system_action

file_app = typer.Typer(help="Local file operations.")
remind_app = typer.Typer(help="Local reminders.")
git_app = typer.Typer(help="Shortcuts over installed Git.")
task_app = typer.Typer(help="Local tasks.")

app = typer.Typer(
    name="beton",
    help="BETON — solid tools for your computer.",
    no_args_is_help=False,
    invoke_without_command=True,
    add_completion=True,
)
app.add_typer(file_app, name="file")
app.add_typer(remind_app, name="remind")
app.add_typer(git_app, name="git")
app.add_typer(task_app, name="task")


def version_callback(value: bool) -> None:
    if value:
        typer.echo(f"BETON {__version__}")
        raise typer.Exit()


def _plain(ctx: typer.Context) -> bool:
    return bool(ctx.ensure_object(dict).get("plain", False))


def _dry_run(ctx: typer.Context) -> bool:
    return bool(ctx.ensure_object(dict).get("dry_run", False))


def _finish(result, *, plain: bool = False) -> None:
    render_result(result, plain=plain)
    if not result.ok:
        raise typer.Exit(code=1)


@app.callback()
def main_callback(
    ctx: typer.Context,
    plain: bool = typer.Option(False, "--plain", help="Disable color and decorative output."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Describe the action without executing it."),
    verbose: bool = typer.Option(False, "--verbose", help="Show additional execution details."),
    version: Optional[bool] = typer.Option(None, "--version", callback=version_callback, is_eager=True),
) -> None:
    """BETON — your computer, one command away."""
    ctx.ensure_object(dict)
    ctx.obj.update(plain=plain, dry_run=dry_run, verbose=verbose)
    if ctx.invoked_subcommand is None:
        render_brand(plain=plain)
        Console(no_color=plain).print(
            "\nTry:\n"
            "  beton open chrome\n"
            "  beton search \"electrostatics\"\n"
            "  beton note \"finish physics DPP\"\n"
            "  beton timer 25\n\n"
            "Run [bold]beton help[/bold] for examples or [bold]beton --help[/bold] for all commands."
        )


@app.command("help")
def help_command(ctx: typer.Context) -> None:
    """Show example-driven Beton help."""
    plain = _plain(ctx)
    out = Console(no_color=plain)
    out.print("BETON — your computer, one command away.\n")
    out.print("[bold]Core commands[/bold]")
    rows = [
        ["open", "Open an app, URL, file, or folder", "beton open chrome"],
        ["search", "Search the web", "beton search \"electrostatics\""],
        ["note", "Save a local Markdown note", "beton note \"finish physics DPP\""],
        ["timer", "Start a countdown", "beton timer 25"],
        ["clip", "Read the text clipboard", "beton clip"],
        ["today", "Show today’s local notes", "beton today"],
        ["doctor", "Check local capabilities", "beton doctor"],
    ]
    render_table("Commands", ["Command", "Purpose", "Example"], rows, plain=plain)
    out.print("\nEach command has its own help: [bold]beton <command> --help[/bold]")


@app.command("open")
def open_command(
    ctx: typer.Context,
    target: str = typer.Argument(..., help="Application alias, URL, file, or folder."),
    browser: str = typer.Option("default", "--browser", help="Browser for URL targets."),
    incognito: bool = typer.Option(False, "--incognito", help="Open an explicit browser privately."),
) -> None:
    """Open an application, URL, file, or folder."""
    try:
        resolved = resolve_target(target)
        adapter = get_adapter()
        if resolved.kind == "url":
            result = adapter.open_url(resolved.value, browser, incognito, _dry_run(ctx))
        elif resolved.kind == "path":
            result = adapter.open_path(Path(resolved.value), _dry_run(ctx))
        else:
            app_target = {"chrome": "google-chrome", "code": "code", "spotify": "spotify"}.get(
                resolved.value.lower(), resolved.value
            )
            result = adapter.launch_app(app_target, _dry_run(ctx))
        _finish(result, plain=_plain(ctx))
    except BetonError as exc:
        Console(stderr=True, no_color=_plain(ctx)).print(f"✕ {exc}")
        raise typer.Exit(code=1) from exc


@app.command("search")
def search_command(
    ctx: typer.Context,
    query: str = typer.Argument(..., help="Text to search for."),
    engine: str = typer.Option("google", "--engine", "-e", help="Search engine."),
    browser: str = typer.Option("default", "--browser", "-b", help="Browser to use."),
    incognito: bool = typer.Option(False, "--incognito", help="Use private browsing mode."),
) -> None:
    """Search the web using an encoded URL."""
    try:
        url = build_search_url(query, engine)
        result = get_adapter().open_url(url, browser, incognito, _dry_run(ctx))
        if result.detail is None:
            result.detail = f"Search URL: {url}"
        _finish(result, plain=_plain(ctx))
    except BetonError as exc:
        Console(stderr=True, no_color=_plain(ctx)).print(f"✕ {exc}")
        raise typer.Exit(code=1) from exc


@app.command("note")
def note_command(
    ctx: typer.Context,
    text: str = typer.Argument(..., help="Text to save locally."),
    tag: Optional[str] = typer.Option(None, "--tag", "-t", help="Optional note tag."),
) -> None:
    """Append a timestamped local Markdown note."""
    if not text.strip():
        raise typer.BadParameter("Note text cannot be empty.")
    path = add_note(text, tag)
    _finish(
        ActionResult(
            ResultStatus.SUCCESS,
            "Saved note locally.",
            detail=str(path),
        ),
        plain=_plain(ctx),
    )


@app.command("timer")
def timer_command(
    ctx: typer.Context,
    duration: str = typer.Argument(..., help="Duration such as 25, 25m, 90s, or 2h."),
    label: Optional[str] = typer.Option(None, "--label", "-l", help="Optional timer label."),
) -> None:
    """Start a foreground countdown timer."""
    try:
        seconds = parse_duration(duration)
    except BetonError as exc:
        Console(stderr=True, no_color=_plain(ctx)).print(f"✕ {exc}")
        raise typer.Exit(code=1) from exc
    title = f" — {label}" if label else ""
    if _dry_run(ctx):
        _finish(
            ActionResult(
                ResultStatus.DRY_RUN,
                f"Would start timer {format_duration(seconds)}{title}.",
            ),
            plain=_plain(ctx),
        )
        return
    console = Console(no_color=_plain(ctx))
    console.print(f"Timer started{title} — {format_duration(seconds)}")
    try:
        for remaining in range(seconds, 0, -1):
            if remaining == seconds or remaining <= 5 or remaining % 60 == 0:
                console.print(f"  {format_duration(remaining)} remaining")
            time.sleep(1)
    except KeyboardInterrupt:
        console.print("Timer stopped.")
        raise typer.Exit(code=130) from None
    console.print("✓ Timer complete.")


@app.command("clip")
def clip_command(ctx: typer.Context, full: bool = typer.Option(False, "--full", help="Do not truncate long text.")) -> None:
    """Read the current text clipboard."""
    plain = _plain(ctx)
    commands = []
    if shutil.which("xclip"):
        commands = ["xclip", "-selection", "clipboard", "-o"]
    elif shutil.which("xsel"):
        commands = ["xsel", "--clipboard", "--output"]
    elif platform.system() == "Darwin" and shutil.which("pbpaste"):
        commands = ["pbpaste"]
    elif platform.system() == "Windows":
        commands = ["powershell", "-NoProfile", "-Command", "Get-Clipboard"]
    if not commands:
        _finish(
            ActionResult(
                ResultStatus.UNAVAILABLE,
                "Clipboard access is unavailable. Install xclip or xsel on Linux, or use the native desktop clipboard.",
            ),
            plain=plain,
        )
        return
    if _dry_run(ctx):
        _finish(
            ActionResult(
                ResultStatus.DRY_RUN,
                "Would read the current text clipboard.",
            ),
            plain=plain,
        )
        return
    try:
        completed = subprocess.run(commands, capture_output=True, text=True, check=True, timeout=5)
    except (OSError, subprocess.SubprocessError) as exc:
        _finish(
            ActionResult(
                ResultStatus.DENIED,
                f"Could not read the clipboard: {exc}",
            ),
            plain=plain,
        )
        return
    value = completed.stdout.rstrip("\n")
    if not full and len(value) > 2000:
        value = value[:2000] + "\n[truncated; use --full to show everything]"
    Console(no_color=plain).print(value or "Clipboard is empty.")


@app.command("clip-set")
def clip_set_command(ctx: typer.Context, value: str) -> None:
    """Set the text clipboard."""
    _finish(write_clipboard(value, _dry_run(ctx)), plain=_plain(ctx))


@app.command("clip-clear")
def clip_clear_command(ctx: typer.Context) -> None:
    """Clear the text clipboard."""
    _finish(clear_clipboard(_dry_run(ctx)), plain=_plain(ctx))


@app.command("clip-history")
def clip_history_command(ctx: typer.Context) -> None:
    """Show local clipboard history collected by explicit clipboard reads."""
    rows = [[str(index), value[:200]] for index, value in enumerate(clipboard_history(), start=1)]
    render_table("Clipboard history", ["#", "Text"], rows or [["—", "No local history"]], plain=_plain(ctx))


@app.command("path")
def path_command(ctx: typer.Context, kind: str = typer.Option("data", "--kind", help="Path kind: data, config, or notes.")) -> None:
    """Show Beton’s local data paths."""
    paths = {"data": data_dir(), "config": config_path(), "notes": notes_path()}
    if kind not in paths:
        raise typer.BadParameter("Choose one of: data, config, notes")
    Console(no_color=_plain(ctx)).print(paths[kind])


@app.command("today")
def today_command(ctx: typer.Context) -> None:
    """Show local notes created today."""
    rows = [[str(index), note.removeprefix("- ")] for index, note in enumerate(today_notes(), start=1)]
    if not rows:
        Console(no_color=_plain(ctx)).print("No notes recorded today.")
        return
    render_table("Today", ["#", "Note"], rows, plain=_plain(ctx))


@task_app.command("add")
def task_add_command(ctx: typer.Context, text: str) -> None:
    """Create a local task."""
    item = add_task(text)
    _finish(ActionResult(ResultStatus.SUCCESS, f"Created task {item['id']}."), plain=_plain(ctx))


@task_app.command("list")
def task_list_command(ctx: typer.Context, all_items: bool = typer.Option(False, "--all")) -> None:
    """List local tasks."""
    rows = [[str(item.get("id")), str(item.get("text"))] for item in list_tasks(all_items)]
    render_table("Tasks", ["ID", "Text"], rows or [["—", "No tasks"]], plain=_plain(ctx))


@task_app.command("done")
def task_done_command(ctx: typer.Context, identifier: str) -> None:
    """Complete a local task."""
    item = complete_task(identifier)
    _finish(ActionResult(ResultStatus.SUCCESS, f"Completed task {identifier}.") if item else ActionResult(ResultStatus.UNAVAILABLE, f"Task not found: {identifier}"), plain=_plain(ctx))


@task_app.command("cancel")
def task_cancel_command(ctx: typer.Context, identifier: str) -> None:
    """Cancel a local task."""
    item = cancel_task(identifier)
    _finish(ActionResult(ResultStatus.SUCCESS, f"Cancelled task {identifier}.") if item else ActionResult(ResultStatus.UNAVAILABLE, f"Task not found: {identifier}"), plain=_plain(ctx))


@app.command("weather")
def weather_command(ctx: typer.Context, location: str = typer.Argument("", help="City or location.")) -> None:
    """Show current weather through the optional wttr.in provider."""
    _finish(weather(location, _dry_run(ctx)), plain=_plain(ctx))


@remind_app.command("add")
def reminder_add_command(
    ctx: typer.Context,
    text: str = typer.Argument(..., help="Reminder text."),
    in_time: Optional[str] = typer.Option(None, "--in", help="Relative time such as 30m, 2h, or 1d."),
    at: Optional[str] = typer.Option(None, "--at", help="ISO date/time such as 2026-08-18T09:00."),
) -> None:
    """Create a local reminder."""
    if bool(in_time) == bool(at):
        raise typer.BadParameter("Choose exactly one of --in or --at.")
    due = parse_due(in_time or at or "")
    item = add_reminder(text, due)
    _finish(ActionResult(ResultStatus.SUCCESS, f"Created reminder {item['id']}.", detail=str(item['due'])), plain=_plain(ctx))


@remind_app.command("list")
def reminder_list_command(ctx: typer.Context, all_items: bool = typer.Option(False, "--all")) -> None:
    """List local reminders."""
    rows = [[str(item.get("id")), str(item.get("due")), str(item.get("text"))] for item in list_reminders(all_items)]
    render_table("Reminders", ["ID", "Due", "Text"], rows or [["—", "—", "No reminders"]], plain=_plain(ctx))


@remind_app.command("done")
def reminder_done_command(ctx: typer.Context, identifier: str) -> None:
    """Mark a reminder complete."""
    item = complete_reminder(identifier)
    if not item:
        _finish(ActionResult(ResultStatus.UNAVAILABLE, f"Reminder not found: {identifier}"), plain=_plain(ctx))
        return
    _finish(ActionResult(ResultStatus.SUCCESS, f"Completed reminder {identifier}."), plain=_plain(ctx))


@remind_app.command("cancel")
def reminder_cancel_command(ctx: typer.Context, identifier: str) -> None:
    """Cancel a reminder."""
    item = cancel_reminder(identifier)
    if not item:
        _finish(ActionResult(ResultStatus.UNAVAILABLE, f"Reminder not found: {identifier}"), plain=_plain(ctx))
        return
    _finish(ActionResult(ResultStatus.SUCCESS, f"Cancelled reminder {identifier}."), plain=_plain(ctx))


@file_app.command("open")
def file_open_command(ctx: typer.Context, path: Path) -> None:
    """Open a local file or folder."""
    _finish(get_adapter().open_path(path.expanduser(), _dry_run(ctx)), plain=_plain(ctx))


@file_app.command("copy")
def file_copy_command(ctx: typer.Context, source: Path, destination: Path) -> None:
    """Copy a file or folder."""
    _finish(copy_path(source.expanduser(), destination.expanduser(), _dry_run(ctx)), plain=_plain(ctx))


@file_app.command("move")
def file_move_command(ctx: typer.Context, source: Path, destination: Path) -> None:
    """Move a file or folder."""
    _finish(move_path(source.expanduser(), destination.expanduser(), _dry_run(ctx)), plain=_plain(ctx))


@file_app.command("rename")
def file_rename_command(ctx: typer.Context, source: Path, name: str) -> None:
    """Rename a local file or folder."""
    _finish(rename_path(source.expanduser(), name, _dry_run(ctx)), plain=_plain(ctx))


@file_app.command("trash")
def file_trash_command(ctx: typer.Context, source: Path, yes: bool = typer.Option(False, "--yes")) -> None:
    """Move a local path to the system trash where supported."""
    if not _dry_run(ctx) and not yes:
        typer.confirm(f"Move {source} to trash", abort=True)
    _finish(trash_path(source.expanduser(), _dry_run(ctx)), plain=_plain(ctx))


@app.command("ask")
def ask_command(ctx: typer.Context, prompt: str) -> None:
    """Ask the optional configured AI provider a question."""
    try:
        answer = complete(prompt)
    except BetonError as exc:
        Console(stderr=True, no_color=_plain(ctx)).print(f"✕ {exc}")
        raise typer.Exit(code=1) from exc
    Console(no_color=_plain(ctx)).print(answer)


@app.command("explain")
def explain_command(ctx: typer.Context, text: str) -> None:
    """Ask the optional AI provider for an explanation."""
    try:
        answer = complete(text, "Explain clearly and briefly, using examples when useful.")
    except BetonError as exc:
        Console(stderr=True, no_color=_plain(ctx)).print(f"✕ {exc}")
        raise typer.Exit(code=1) from exc
    Console(no_color=_plain(ctx)).print(answer)


@app.command("rewrite")
def rewrite_command(ctx: typer.Context, text: str) -> None:
    """Rewrite text through the optional AI provider."""
    try:
        answer = complete(text, "Rewrite the user text clearly while preserving its meaning.")
    except BetonError as exc:
        Console(stderr=True, no_color=_plain(ctx)).print(f"✕ {exc}")
        raise typer.Exit(code=1) from exc
    Console(no_color=_plain(ctx)).print(answer)


@app.command("summarize")
def summarize_command(ctx: typer.Context, path: Path) -> None:
    """Summarize a local text or Markdown file through optional AI."""
    try:
        content = path.expanduser().read_text(encoding="utf-8")
        if len(content) > 100_000:
            raise ConfigurationError("File is too large for this command; provide a smaller text or Markdown file.")
        answer = complete(content, "Summarize the provided document with key points and action items.")
    except (OSError, BetonError) as exc:
        Console(stderr=True, no_color=_plain(ctx)).print(f"✕ {exc}")
        raise typer.Exit(code=1) from exc
    Console(no_color=_plain(ctx)).print(answer)


@app.command("translate")
def translate_command(ctx: typer.Context, text: str, to: str = typer.Option(..., "--to")) -> None:
    """Translate text through the optional AI provider."""
    try:
        answer = complete(text, f"Translate the text into {to}. Return only the translation.")
    except BetonError as exc:
        Console(stderr=True, no_color=_plain(ctx)).print(f"✕ {exc}")
        raise typer.Exit(code=1) from exc
    Console(no_color=_plain(ctx)).print(answer)


@app.command("window")
def window_command(
    ctx: typer.Context,
    action: str = typer.Argument(..., help="active or focus."),
    title: Optional[str] = typer.Argument(None, help="Window title for focus."),
) -> None:
    """Inspect or focus desktop windows where supported."""
    if action == "active":
        _finish(active_window(_dry_run(ctx)), plain=_plain(ctx))
        return
    if action == "focus" and title:
        _finish(focus_window(title, _dry_run(ctx)), plain=_plain(ctx))
        return
    raise typer.BadParameter("Use `beton window active` or `beton window focus <title>`." )


@app.command("plugin")
def plugin_command(
    ctx: typer.Context,
    action: str = typer.Argument("list", help="list, enable, or disable."),
    name: Optional[str] = typer.Argument(None, help="Plugin name."),
) -> None:
    """List or toggle optional local integrations."""
    if action == "list":
        rows = [[str(item.get("name")), "enabled" if item.get("enabled") else "disabled"] for item in list_plugins()]
        render_table("Plugins", ["Name", "Status"], rows or [["—", "No plugins registered"]], plain=_plain(ctx))
        return
    if action not in {"enable", "disable"} or not name:
        raise typer.BadParameter("Use `beton plugin list`, `beton plugin enable <name>`, or `beton plugin disable <name>`." )
    item = set_plugin(name, action == "enable")
    _finish(ActionResult(ResultStatus.SUCCESS, f"Plugin {name} is now {'enabled' if item['enabled'] else 'disabled'}.", detail="Plugin code is not executed automatically."), plain=_plain(ctx))


@app.command("volume")
def volume_command(ctx: typer.Context, value: str = typer.Argument(..., help="0-100 or mute.")) -> None:
    """Set or toggle system volume."""
    _finish(volume(value, _dry_run(ctx)), plain=_plain(ctx))


@app.command("media")
def media_command(ctx: typer.Context, action: str = typer.Argument(..., help="play, pause, next, or previous.")) -> None:
    """Control media playback."""
    if action not in {"play", "pause", "next", "previous"}:
        raise typer.BadParameter("Choose one of: play, pause, next, previous")
    _finish(media(action, _dry_run(ctx)), plain=_plain(ctx))


@app.command("battery")
def battery_command(ctx: typer.Context) -> None:
    """Show battery status."""
    _finish(battery(_dry_run(ctx)), plain=_plain(ctx))


@app.command("wifi")
def wifi_command(ctx: typer.Context) -> None:
    """Show Wi-Fi status."""
    _finish(network_info("wifi", dry_run=_dry_run(ctx)), plain=_plain(ctx))


@app.command("ip")
def ip_command(ctx: typer.Context) -> None:
    """Show network interface information."""
    _finish(network_info("ip", dry_run=_dry_run(ctx)), plain=_plain(ctx))


@app.command("ping")
def ping_command(ctx: typer.Context, target: str) -> None:
    """Ping a host once."""
    _finish(network_info("ping", target, _dry_run(ctx)), plain=_plain(ctx))


@app.command("dns")
def dns_command(ctx: typer.Context, target: str) -> None:
    """Look up DNS information for a host."""
    _finish(network_info("dns", target, _dry_run(ctx)), plain=_plain(ctx))


@git_app.command("status")
def git_status_command(ctx: typer.Context, path: Path = typer.Option(Path.cwd(), "--path")) -> None:
    """Run git status in a project directory."""
    if _dry_run(ctx):
        _finish(ActionResult(ResultStatus.DRY_RUN, f"Would run git status in {path.expanduser()}."), plain=_plain(ctx))
        return
    try:
        completed = subprocess.run(["git", "-C", str(path.expanduser()), "status", "--short", "--branch"], capture_output=True, text=True, check=False, timeout=8)
    except (OSError, subprocess.SubprocessError) as exc:
        _finish(ActionResult(ResultStatus.UNAVAILABLE, f"Git is unavailable: {exc}"), plain=_plain(ctx))
        return
    _finish(ActionResult(ResultStatus.SUCCESS if completed.returncode == 0 else ResultStatus.DENIED, "Git status", detail=completed.stdout.strip() or completed.stderr.strip()), plain=_plain(ctx))


@app.command("find")
def find_command(
    ctx: typer.Context,
    pattern: str = typer.Argument(..., help="Filename or glob pattern."),
    root: Path = typer.Option(Path.home(), "--in", help="Directory to search; defaults to the home directory."),
    limit: int = typer.Option(50, "--limit", min=1, max=500, help="Maximum results."),
) -> None:
    """Find files below an explicit search root."""
    results = find_files(pattern, root.expanduser(), limit)
    if not results:
        Console(no_color=_plain(ctx)).print(f"No files found below {root}.")
        return
    render_table("Files", ["Path"], [[str(path)] for path in results], plain=_plain(ctx))


@app.command("kill")
def kill_command(
    ctx: typer.Context,
    target: str = typer.Argument(..., help="Process name or PID."),
    force: bool = typer.Option(False, "--force", help="Use forceful termination."),
    yes: bool = typer.Option(False, "--yes", help="Skip confirmation."),
) -> None:
    """Terminate a process after explicit confirmation."""
    if not _dry_run(ctx) and not yes:
        typer.confirm(f"Terminate process {target}", abort=True)
    _finish(terminate_process(target, force, _dry_run(ctx)), plain=_plain(ctx))


@app.command("screenshot")
def screenshot_command(
    ctx: typer.Context,
    path: Optional[Path] = typer.Option(None, "--path", help="Output PNG path."),
) -> None:
    """Capture the current screen where supported."""
    _finish(capture(path.expanduser() if path else None, _dry_run(ctx)), plain=_plain(ctx))


@app.command("process")
def process_command(
    ctx: typer.Context,
    query: Optional[str] = typer.Argument(None, help="Optional process-name filter."),
    limit: int = typer.Option(50, "--limit", min=1, max=200, help="Maximum results."),
) -> None:
    """List local processes without modifying them."""
    rows = process_rows(query, limit)
    if not rows:
        Console(no_color=_plain(ctx)).print("No matching processes found or process listing is unavailable.")
        return
    render_table("Processes", ["PID", "Command", "Arguments"], rows, plain=_plain(ctx))


@app.command("system")
def system_command(
    ctx: typer.Context,
    action: str = typer.Argument(..., help="lock, sleep, logout, restart, or shutdown."),
    yes: bool = typer.Option(False, "--yes", help="Skip the confirmation prompt for disruptive actions."),
) -> None:
    """Control the local session or system power state."""
    allowed = {"lock", "sleep", "logout", "restart", "shutdown"}
    if action not in allowed:
        raise typer.BadParameter("Choose one of: lock, sleep, logout, restart, shutdown")
    if not _dry_run(ctx) and action != "lock" and not yes:
        typer.confirm(f"Confirm system action '{action}'", abort=True)
    _finish(system_action(action, dry_run=_dry_run(ctx)), plain=_plain(ctx))


@app.command("apps")
def apps_command(ctx: typer.Context) -> None:
    """List configured application aliases."""
    config = load_config()
    rows = []
    for alias, entry in sorted(config.get("aliases", {}).items()):
        if isinstance(entry, dict) and entry.get("kind") == "app":
            value = str(entry.get("value", ""))
            rows.append([alias, value, "detected" if shutil.which(value) else "not on PATH"])
    render_table("Application aliases", ["Alias", "Target", "Status"], rows or [["—", "No app aliases", "configure in config.json"]], plain=_plain(ctx))


@app.command("config")
def config_command(
    ctx: typer.Context,
    action: str = typer.Argument("show", help="show or set."),
    key: Optional[str] = typer.Argument(None, help="Setting name when using set."),
    value: Optional[str] = typer.Argument(None, help="Setting value when using set."),
) -> None:
    """Show or update local Beton configuration."""
    plain = _plain(ctx)
    if action == "show":
        config = load_config()
        Console(no_color=plain).print_json(data=config)
        return
    if action != "set" or key is None or value is None:
        raise typer.BadParameter("Use `beton config show` or `beton config set <key> <value>`." )
    typed_value: object = value.lower() == "true" if value.lower() in {"true", "false"} else value
    updated = set_config_value(key, typed_value)
    Console(no_color=plain).print(f"✓ Updated {key}.")
    if ctx.ensure_object(dict).get("verbose"):
        Console(no_color=plain).print_json(data=updated)


@app.command("doctor")
def doctor_command(ctx: typer.Context) -> None:
    """Check Beton’s local runtime and platform capabilities."""
    rows = [
        ["Python", platform.python_version(), "ok"],
        ["Operating system", platform.platform(), "ok"],
        ["Data directory", str(data_dir()), "writable" if data_dir().exists() or data_dir().parent.exists() else "not created"],
        ["xdg-open", "available" if shutil.which("xdg-open") else "missing", "Linux path opener"],
        ["Google Chrome", "available" if any(shutil.which(x) for x in ["google-chrome", "google-chrome-stable", "chrome"]) else "not found", "optional"],
        ["Microsoft Edge", "available" if any(shutil.which(x) for x in ["microsoft-edge", "msedge"]) else "not found", "optional"],
        ["Firefox", "available" if shutil.which("firefox") else "not found", "optional"],
    ]
    render_table("BETON diagnostics", ["Check", "Value", "Detail"], rows, plain=_plain(ctx))


if __name__ == "__main__":
    app()


def main() -> None:
    """Console-script entry point."""
    app()
