"""`mechas session` — the Keeper's surface (G4, decision record 0021).

The session lab (`labs/game_loop/session_runner.py`) owns every rule:
eras are real `runtime.evolve` runs, unlocks are facts citing report
metrics, extinction and succession are engine contracts. This command is
the supportive layer (DR 0007's charter): it drives the lab's CLI modes
in the WORKSPACE interpreter, narrates the JSON it gets back, and can
serve the Keeper page on the workshop server.
"""

from __future__ import annotations

import json
import subprocess
import time
import webbrowser
from pathlib import Path

import typer

from mechas_cli import theme
from mechas_cli.workflows.rate import _workspace_python
from mechas_cli.workflows.workshop import launch_workshop_server
from mechas_cli.workspace import find_workspace_root


SESSION_LAB = Path("labs") / "game_loop" / "session_runner.py"


def session(
    status: bool = typer.Option(
        False, "--status", help="Where the bloodline stands."
    ),
    new: bool = typer.Option(
        False, "--new", help="Start a keeper session (one per workspace)."
    ),
    era: str | None = typer.Option(
        None,
        "--era",
        help="Run one era under this forecast: calm, stable_soup, or "
        "storm — a real evolve run, persisted.",
    ),
    open_page: bool = typer.Option(
        False,
        "--open",
        help="Serve the Keeper page (workshop server) and open it.",
    ),
    port: int = typer.Option(
        0, "--port", help="Local port for --open (default: pick a free one)."
    ),
) -> None:
    """The Keeper's session: eras, weather, unlocks — engine truth."""
    console = theme.console()
    root = find_workspace_root()

    if open_page:
        console.print(theme.banner("session — the Keeper's surface"))
        process, page_url = launch_workshop_server(
            console, root, port, "session"
        )
        console.print(
            theme.kv_table(
                [
                    ("keeper page", page_url, "mechas.path"),
                    (
                        "every number",
                        "a report field from a real evolve run — "
                        "the page never invents one",
                        "mechas.ok",
                    ),
                    (
                        "state",
                        "data/game_loop/keeper/ "
                        "(state + the DR 0022 ledger, backup before "
                        "overwrite)",
                        "mechas.path",
                    ),
                ]
            )
        )
        console.print()
        console.print(
            "  [mechas.dim]play in the browser — this window waits. "
            "Press Ctrl+C when you're done.[/]"
        )
        webbrowser.open(page_url)
        try:
            while process.poll() is None:
                time.sleep(0.5)
            console.print("  [mechas.warn]the workshop server exited.[/]")
        except KeyboardInterrupt:
            process.terminate()
        console.print()
        console.print("  [mechas.dim]session closed.[/]")
        return

    if new:
        _lab(console, root, ["--mode", "new"], _print_summary)
        return
    if era is not None:
        _lab(
            console,
            root,
            ["--mode", "advance", "--weather", era],
            _print_turn,
        )
        return
    if status:
        _lab(console, root, ["--mode", "status"], _print_summary)
        return

    console.print(theme.banner("session — what would you like to do?"))
    console.print(
        theme.kv_table(
            [
                ("target", "--open", "mechas.accent"),
                (
                    "what",
                    "serve the Keeper page: campaign, weather picker, "
                    "era history, unlocks",
                    "mechas.value",
                ),
                ("target", "--era <forecast>", "mechas.accent"),
                (
                    "what",
                    "run one era from the terminal (calm, stable_soup, "
                    "storm) — a real evolve run, persisted",
                    "mechas.value",
                ),
                ("target", "--status", "mechas.accent"),
                (
                    "what",
                    "where the bloodline stands: eras, unlocks, "
                    "extinctions",
                    "mechas.value",
                ),
                ("target", "--new", "mechas.accent"),
                ("what", "start the keeper session", "mechas.value"),
                (
                    "saves to",
                    "data/game_loop/keeper/ (state + the DR 0022 "
                    "campaign ledger)",
                    "mechas.path",
                ),
            ]
        )
    )
    console.print()
    console.print(
        "  [mechas.dim]try:[/]  [mechas.accent]mechas session --open[/]"
        "  [mechas.dim]or[/]  [mechas.accent]mechas session --era storm[/]"
    )


def _lab(console, root, args: list[str], render) -> None:
    """Run the session lab's CLI mode in the workspace interpreter."""
    completed = subprocess.run(
        [_workspace_python(root), "-B", str(root / SESSION_LAB), *args],
        cwd=root,
        capture_output=True,
        text=True,
    )
    try:
        result = json.loads(completed.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError):
        console.print(
            "[mechas.err]The session lab couldn't run.[/] Details:\n"
            + (completed.stderr or completed.stdout or "(no output)")
        )
        raise typer.Exit(code=1)
    if not result.get("ok"):
        console.print(
            "[mechas.err]" + str(result.get("error", "session failed")) + "[/]"
        )
        raise typer.Exit(code=1)
    render(console, result)


def _print_summary(console, result: dict) -> None:
    console.print(theme.banner("session — the bloodline"))
    entries: list[tuple[str, str, str]] = []
    for campaign in result.get("campaigns", []):
        flavor = "mechas.ok" if campaign["status"] == "active" else "mechas.err"
        marker = (
            " (active)"
            if campaign["campaign_id"] == result.get("active_campaign_id")
            else ""
        )
        entries.append(
            (
                campaign["campaign_id"] + marker,
                f"{campaign['status']} · {campaign['era_count']} eras · "
                f"covenant {campaign['profile_id']} · "
                f"{len(campaign['unlocks'])} unlocks earned",
                flavor,
            )
        )
    entries.append(
        (
            "unlock state",
            f"{len(result.get('unlock_state', []))} facts carried by the "
            "active bloodline",
            "mechas.value",
        )
    )
    console.print(theme.kv_table(entries))
    console.print()
    console.print(
        "  [mechas.dim]next:[/]  [mechas.accent]mechas session --era storm[/]"
        "  [mechas.dim]or[/]  [mechas.accent]mechas session --open[/]"
    )


def _print_turn(console, result: dict) -> None:
    era = result["era"]
    console.print(theme.banner(f"session — era {era['era_index']} complete"))
    entries = [
        ("forecast", era["forecast"], "mechas.accent"),
        (
            "the soup",
            f"{era['total_removed_cells']} cells wrecked"
            + (
                f" · survived {era['max_dropout_multiplier_survived']:.2f}x "
                "weather"
                if era["max_dropout_multiplier_survived"]
                else ""
            ),
            "mechas.value",
        ),
        (
            "bloodline",
            (
                f"{era['founders_admitted']} founders admitted through the "
                "engine's gates"
                if era["founders_admitted"]
                else "seeded from the corpus"
            )
            + f" · lineage depth {era['max_lineage_generation']}",
            "mechas.value",
        ),
        (
            "archive",
            f"{era['filled_niches']} niches · QD {era['qd_score']:.2f}",
            "mechas.value",
        ),
        (
            "unlocks earned",
            ", ".join(
                f"{fact['axis']} tier {fact['tier']}"
                for fact in result["unlocks_earned"]
            )
            or "none this era",
            "mechas.ok" if result["unlocks_earned"] else "mechas.dim",
        ),
    ]
    if era["went_extinct"]:
        succession = result.get("succession") or {}
        entries.append(
            (
                "THE BLOODLINE ENDED",
                f"{succession.get('successor_campaign_id', '?')} carries "
                f"{succession.get('carried_unlock_count', 0)} unlock(s) — "
                "the soup remembers nothing else",
                "mechas.err",
            )
        )
    console.print(theme.kv_table(entries))
    console.print()
    console.print(
        "  [mechas.dim]review it:[/]  [mechas.accent]mechas workshop "
        "--preview[/] [mechas.dim](record a replay — the scrubber is the "
        "window)[/]"
    )
