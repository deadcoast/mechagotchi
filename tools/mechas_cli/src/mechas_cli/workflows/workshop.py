"""`mechas workshop` — serving the creative authoring layer.

`mechas workshop --editor` launches the grid editor: the workshop server
runs in the WORKSPACE interpreter (it imports the engine for live
validation — the CLI's isolated environment cannot), mechas supervises
it, opens the browser, and narrates. The workshop is application content;
this command is its supportive serving surface (charter:
docs/workshop/mecha-workshop-design.md).
"""

from __future__ import annotations

import subprocess
import time
import urllib.error
import urllib.request
import webbrowser
from pathlib import Path

import typer

from mechas_cli import theme
from mechas_cli.workflows.rate import _workspace_python
from mechas_cli.workspace import find_workspace_root


SERVER_SCRIPT = Path("workshop") / "server" / "workshop_server.py"
# Port 0 = the OS picks a free port. Windows reserves shifting port
# ranges (WinError 10013 on bind), so hardcoded defaults are fragile;
# the server announces its real URL and the launcher reads it.
DEFAULT_PORT = 0


def workshop(
    editor: bool = typer.Option(
        False,
        "--editor",
        help="Launch the grid editor with live engine validation.",
    ),
    port: int = typer.Option(
        DEFAULT_PORT,
        "--port",
        help="Local port for the workshop (default: pick a free one).",
    ),
    open_browser: bool = typer.Option(
        True,
        "--browser/--no-browser",
        help="Open the workshop in your browser automatically.",
    ),
) -> None:
    """The creative authoring layer. Start with [bold]--editor[/bold]."""
    console = theme.console()
    root = find_workspace_root()

    if not editor:
        console.print(theme.banner("workshop — what would you like to open?"))
        console.print(
            theme.kv_table(
                [
                    ("target", "--editor", "mechas.accent"),
                    (
                        "what",
                        "draw a creature on the grid; the engine validates "
                        "live and explains every constraint",
                        "mechas.value",
                    ),
                    (
                        "saves to",
                        "data/workshop/grids/ (engine-valid grids only, "
                        "backup before overwrite)",
                        "mechas.path",
                    ),
                ]
            )
        )
        console.print()
        console.print(
            "  [mechas.dim]try:[/]  [mechas.accent]mechas workshop --editor[/]"
        )
        return

    console.print(theme.banner("workshop --editor — grid editor"))
    server_path = root / SERVER_SCRIPT
    if not server_path.exists():
        console.print(
            f"[mechas.err]The workshop server is missing[/] "
            f"([mechas.path]{SERVER_SCRIPT}[/]) — the workspace may be "
            "incomplete."
        )
        raise typer.Exit(code=1)

    process = subprocess.Popen(
        [_workspace_python(root), "-B", str(server_path), "--port", str(port)],
        cwd=root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    # The server announces its real URL (the engine import takes a
    # moment, then the announcement line arrives; port 0 support means
    # the launcher never guesses).
    url = None
    announced = process.stdout.readline() if process.stdout else ""
    if "http://" in announced:
        url = announced.strip().split()[-1]
    ready = False
    if url:
        for _ in range(40):
            if process.poll() is not None:
                break
            try:
                with urllib.request.urlopen(url, timeout=0.5):
                    ready = True
                    break
            except (urllib.error.URLError, OSError):
                time.sleep(0.25)
    if not ready:
        stderr = process.stderr.read() if process.stderr else ""
        process.terminate()
        if "10048" in stderr or "10013" in stderr:
            console.print(
                f"[mechas.err]Port {port} is unavailable[/] (busy, or in a "
                "Windows-reserved range). Try "
                "[mechas.accent]mechas workshop --editor[/] without --port "
                "to pick a free one automatically."
            )
        else:
            console.print(
                "[mechas.err]The workshop couldn't start.[/] Details:\n"
                + (stderr or "(no output)")
            )
        raise typer.Exit(code=1)

    console.print(
        theme.kv_table(
            [
                ("grid editor", url, "mechas.path"),
                (
                    "validation",
                    "live, from the engine itself — errors are the "
                    "engine's own words",
                    "mechas.ok",
                ),
                (
                    "saving",
                    "engine-valid grids only → data/workshop/grids/",
                    "mechas.value",
                ),
            ]
        )
    )
    console.print()
    console.print(
        "  [mechas.dim]draw in the browser — this window waits. Press "
        "Ctrl+C when you're done.[/]"
    )
    if open_browser:
        webbrowser.open(url)

    try:
        while process.poll() is None:
            time.sleep(0.5)
        console.print("  [mechas.warn]the workshop server exited.[/]")
    except KeyboardInterrupt:
        process.terminate()
    console.print()
    console.print("  [mechas.dim]workshop closed.[/]")
