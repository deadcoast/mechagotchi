"""`mechas game` — the playable client (Phase F, decision record 0033).

The game build (`game/`) owns every rule: the companion loop, eras,
the covenant, the hatchery, the review — all engine truth. This
command is the supportive layer (DR 0007's charter: new operational
workflows become `mechas` commands): it launches, builds, and
regenerates evidence for the client with the WORKSPACE interpreter
(the game group's pygame-ce lives in the workspace venv).
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import typer

from mechas_cli import theme
from mechas_cli.workflows.rate import _workspace_python
from mechas_cli.workspace import find_workspace_root


GAME_LAUNCHER = Path("game") / "run_game.py"
GAME_BUILDER = Path("game") / "build_release.py"
GAME_EVIDENCE = Path("game") / "evidence.py"


def game(
    play: bool = typer.Option(
        False, "--play", help="Launch the Mechagotchi client and play."
    ),
    ticks: int | None = typer.Option(
        None,
        "--ticks",
        help="Bounded verification run (with --play): quit after N "
        "lifecycle ticks.",
    ),
    new: bool = typer.Option(
        False,
        "--new",
        help="Start a fresh companion instead of resuming the save.",
    ),
    build: bool = typer.Option(
        False,
        "--build",
        help="Build the installable release (PyInstaller, DR 0033).",
    ),
    windowed: bool = typer.Option(
        False,
        "--windowed",
        help="Build without a console window (with --build).",
    ),
    evidence: bool = typer.Option(
        False,
        "--evidence",
        help="Regenerate the game's stage-0 evidence artifacts "
        "(data/game_client/).",
    ),
) -> None:
    """Play, build, or verify the Mechagotchi game client."""
    console = theme.console()
    root = find_workspace_root()
    python = _workspace_python(root)

    if not (play or build or evidence):
        console.print(
            theme.banner("game — the playable Mechagotchi client")
        )
        console.print(
            "Pick one: [bold]--play[/] (launch it), [bold]--build[/] "
            "(the installable release), [bold]--evidence[/] "
            "(regenerate the stage-0 artifacts)."
        )
        raise typer.Exit(0)

    if play:
        command = [python, "-B", str(root / GAME_LAUNCHER)]
        if ticks is not None:
            command += ["--ticks", str(ticks)]
        if new:
            command.append("--new")
        console.print(theme.banner("game — launching the client"))
        result = subprocess.run(command, cwd=root)
        raise typer.Exit(result.returncode)

    if build:
        command = [python, "-B", str(root / GAME_BUILDER)]
        if windowed:
            command.append("--windowed")
        console.print(theme.banner("game — building the release"))
        result = subprocess.run(command, cwd=root)
        if result.returncode == 0:
            console.print(
                "built: [bold]game/dist/Mechagotchi/[/] — launch the "
                "executable inside"
            )
        raise typer.Exit(result.returncode)

    console.print(theme.banner("game — regenerating evidence"))
    result = subprocess.run(
        [python, "-B", str(root / GAME_EVIDENCE)], cwd=root
    )
    raise typer.Exit(result.returncode)
