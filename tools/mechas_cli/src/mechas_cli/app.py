"""`mechas` — the Mechagotchi companion CLI (root command)."""

from __future__ import annotations

import json

import typer

from mechas_cli import __version__, theme
from mechas_cli.workspace import WorkspaceNotFoundError, find_workspace_root
from mechas_cli.workflows.rate import rate
from mechas_cli.workflows.session import session
from mechas_cli.workflows.workshop import workshop


app = typer.Typer(
    name="mechas",
    rich_markup_mode="rich",
    no_args_is_help=True,
    add_completion=False,
    help=(
        "[bold #d8ffd6]mechas[/] — the Mechagotchi companion CLI.\n\n"
        "One standard front door for the workspace: every command walks "
        "you through a whole task, saves its results into the project, "
        "and tells you what to do next."
    ),
    epilog=(
        "Start with [bold #5dbb63]mechas rate --creatures[/] to rate the "
        "creature samples, or [bold #5dbb63]mechas status[/] to see where "
        "the project stands."
    ),
)

app.command(name="rate")(rate)
app.command(name="session")(session)
app.command(name="workshop")(workshop)


@app.command()
def status() -> None:
    """Where the project stands: modules, gates, and open human tasks."""
    console = theme.console()
    root = find_workspace_root()
    console.print(theme.banner("status — the workspace at a glance"))

    entries: list[tuple[str, str, str]] = []
    promotion = (
        root
        / "data"
        / "package_promotion"
        / "mecha_engine_package_promotion_gate_stage0.json"
    )
    if promotion.exists():
        summary = json.loads(promotion.read_text(encoding="utf-8")).get(
            "summary", {}
        )
        entries.append(
            (
                "engine modules",
                f"{summary.get('promotion_ready_count', '?')} promotion-ready "
                f"of {summary.get('candidate_count', '?')} candidates",
                "mechas.ok",
            )
        )
    calibration = (
        root
        / "data"
        / "readability"
        / "slip_readability_calibration_gate_stage0.json"
    )
    if calibration.exists():
        gate = json.loads(calibration.read_text(encoding="utf-8"))
        ready = bool(gate.get("manual_readability_calibration_ready"))
        entries.append(
            (
                "readability calibration",
                "ready" if ready else "waiting on human ratings — "
                "run [bold]mechas rate --creatures[/]",
                "mechas.ok" if ready else "mechas.warn",
            )
        )
    if not entries:
        entries.append(
            ("workspace", "no gate artifacts found yet", "mechas.warn")
        )
    console.print(theme.kv_table(entries))


@app.callback(invoke_without_command=True)
def _root(
    version: bool = typer.Option(
        False,
        "--version",
        help="Show the mechas version and exit.",
        is_eager=True,
    ),
) -> None:
    if version:
        console = theme.console()
        console.print(f"[mechas.title]mechas[/] [mechas.dim]{__version__}[/]")
        raise typer.Exit()


def main() -> None:
    try:
        app()
    except WorkspaceNotFoundError as error:
        console = theme.console()
        console.print(f"[mechas.err]{error}[/]")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
