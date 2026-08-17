"""Terminal rendering helpers with a plain-mode fallback."""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .models import ActionResult, ResultStatus


def console(plain: bool = False) -> Console:
    return Console(no_color=plain, highlight=False)


def render_result(result: ActionResult, *, plain: bool = False) -> None:
    out = console(plain)
    symbols = {
        ResultStatus.SUCCESS: "OK",
        ResultStatus.DRY_RUN: "DRY RUN",
        ResultStatus.DENIED: "DENIED",
        ResultStatus.UNAVAILABLE: "UNAVAILABLE",
        ResultStatus.NEEDS_AUTH: "AUTH REQUIRED",
    }
    label = symbols[result.status]
    if plain:
        out.print(f"[{label}] {result.message}")
    elif result.status in {ResultStatus.SUCCESS, ResultStatus.DRY_RUN}:
        out.print(f"[bold green]✓[/bold green] {result.message}")
    elif result.status == ResultStatus.NEEDS_AUTH:
        out.print(f"[bold yellow]![/bold yellow] {result.message}")
    else:
        out.print(f"[bold red]✕[/bold red] {result.message}")
    if result.detail:
        out.print(result.detail)


def render_brand(*, plain: bool = False) -> None:
    out = console(plain)
    if plain:
        out.print("BETON\nYour computer, one command away.")
        return
    out.print(Panel.fit("[bold white]BETON[/bold white]\n[dim]Your computer, one command away.[/dim]", border_style="bright_black"))


def render_table(title: str, columns: list[str], rows: list[list[str]], *, plain: bool = False) -> None:
    out = console(plain)
    if plain:
        out.print(title)
        for row in rows:
            out.print("\t".join(row))
        return
    table = Table(title=title, show_header=True, header_style="bold cyan")
    for column in columns:
        table.add_column(column)
    for row in rows:
        table.add_row(*row)
    out.print(table)
