"""`mechas` — the Mechagotchi companion CLI (root command)."""

from __future__ import annotations

import typer

from mechas_cli import __version__, theme
from mechas_cli.workspace import WorkspaceNotFoundError, find_workspace_root
from mechas_cli.workflows.develop import develop
from mechas_cli.workflows.game import game
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
        "Start with [bold #5dbb63]mechas game --play[/] to open the "
        "native application, or [bold #5dbb63]mechas status[/] to see where "
        "the project stands."
    ),
)

app.command(name="rate")(rate)
app.command(name="session")(session)
app.command(name="workshop")(workshop)
app.command(name="game")(game)
app.command(name="develop")(develop)


@app.command()
def status(artifact_report: str | None = typer.Option(None, '--artifact-report', help='Inspect a recorded detached Windows artifact report; does not rerun verification.')) -> None:
    """Application, local checks, packaged evidence and separate research calibration."""
    from pathlib import Path
    from mechas_cli.workflows.status import show_status
    show_status(find_workspace_root(), Path(artifact_report) if artifact_report else None)


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
