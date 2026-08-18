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
from .output import render_brand, render_result, render_table
from .platform import get_adapter
from .resolver import resolve_target
from .search import SEARCH_URLS, build_search_url
from .storage.notes import add_note, today_notes
from .timer import format_duration, parse_duration
from .system import system_action
from .upgrade import upgrade as upgrade_checkout

app = typer.Typer(
    name="beton",
    help="BETON — solid tools for your computer.",
    no_args_is_help=False,
    invoke_without_command=True,
    add_completion=True,
)


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
        ["version", "Show version or upgrade the official source", "beton version --upgrade"],
    ]
    render_table("Commands", ["Command", "Purpose", "Example"], rows, plain=plain)
    out.print("\nEach command has its own help: [bold]beton <command> --help[/bold]")
    out.print("Run [bold]beton[/bold] by itself for the brand screen; do not append [bold]beton[/bold] as a subcommand.")


@app.command("version")
def version_command(
    ctx: typer.Context,
    upgrade: bool = typer.Option(False, "--upgrade", help="Update an official source checkout from GitHub."),
    yes: bool = typer.Option(False, "--yes", help="Skip the confirmation prompt for the upgrade."),
) -> None:
    """Show the installed version or update an official source checkout."""
    plain = _plain(ctx)
    out = Console(no_color=plain)
    if not upgrade:
        out.print(f"BETON {__version__}")
        return

    dry_run = _dry_run(ctx)
    try:
        preview = upgrade_checkout(dry_run=True)
        if dry_run:
            out.print(
                f"Would check GitHub and update {preview.root} from {preview.before[:8]} "
                f"using the official {preview.root.name} source checkout."
            )
            return
        if not yes and not typer.confirm(
            f"Update BETON in {preview.root} from GitHub now?", default=True
        ):
            out.print("Upgrade cancelled.")
            return
        result = upgrade_checkout(dry_run=False)
        if result.changed:
            out.print(f"Updated BETON: {result.before[:8]} → {result.after[:8]}")
        else:
            out.print("BETON is already up to date.")
        out.print("The active Python environment now points at the updated source checkout.")
    except BetonError as exc:
        Console(stderr=True, no_color=plain).print(f"✕ {exc}")
        raise typer.Exit(code=1) from exc


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
            if platform.system() == "Windows":
                app_target = resolved.value
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
