"""`mechas rate` — the standardized rating workflow.

`mechas rate --creatures` launches the creature readability rating session:
it serves the visual rating tool locally, opens the browser, receives the
finished ratings back over HTTP, writes them into the project (backing up
anything it would overwrite), and runs the calibration gate — the complete
loop, no files moved by hand.
"""

from __future__ import annotations

import csv
import io
import json
import shutil
import subprocess
import sys
import threading
import time
import webbrowser
from pathlib import Path

import typer
from rich.text import Text

from mechas_cli import theme
from mechas_cli.ratings_server import (
    CSV_HEADER,
    RATINGS_FILENAME,
    start_server,
)
from mechas_cli.workspace import find_workspace_root


TOOL_FILENAME = "slip_readability_calibration_rating_tool.html"
EXPECTED_ROWS = 63
GATE_SCRIPT = Path("labs/readability_benchmark/slip_readability_calibration_gate.py")
TOOL_BUILDER = Path("labs/readability_benchmark/rating_tool_builder.py")


def rate(
    creatures: bool = typer.Option(
        False,
        "--creatures",
        help="Rate the 21 creature samples for readability calibration.",
    ),
    autoexport: bool = typer.Option(
        False,
        "--autoexport",
        help="Save ratings into the project automatically after each "
        "completed reviewer pass — no export click needed.",
    ),
    port: int = typer.Option(
        8423,
        "--port",
        help="Local port for the rating session (0 picks a free one).",
    ),
    open_browser: bool = typer.Option(
        True,
        "--browser/--no-browser",
        help="Open the rating page in your browser automatically.",
    ),
    status: bool = typer.Option(
        False,
        "--status",
        help="Show how far the rating collection has come, then exit.",
    ),
    ingest: Path | None = typer.Option(
        None,
        "--ingest",
        help="Bring a downloaded ratings CSV into the project and run the "
        "calibration gate on it.",
    ),
) -> None:
    """Rate project samples. Start with [bold]--creatures[/bold]."""
    console = theme.console()
    root = find_workspace_root()
    ratings_path = root / "data" / "readability" / RATINGS_FILENAME

    if status:
        _show_status(console, root, ratings_path)
        return
    if ingest is not None:
        _ingest(console, root, ratings_path, ingest)
        return
    if not creatures:
        _show_targets(console, ratings_path)
        return

    _run_session(
        console,
        root,
        ratings_path,
        port=port,
        autoexport=autoexport,
        open_browser=open_browser,
    )


# --------------------------------------------------------------- helpers


def _count_rows(ratings_path: Path) -> tuple[int, list[str]]:
    """(data rows, distinct reviewer ids) in the collected CSV, if any."""
    if not ratings_path.exists():
        return 0, []
    with io.StringIO(ratings_path.read_text(encoding="utf-8")) as handle:
        rows = list(csv.DictReader(handle))
    reviewers = sorted({row.get("reviewer_id", "") for row in rows} - {""})
    return len(rows), reviewers


def _show_targets(console, ratings_path: Path) -> None:
    console.print(theme.banner("rate — what would you like to rate?"))
    rows, reviewers = _count_rows(ratings_path)
    progress = (
        f"{rows}/{EXPECTED_ROWS} rows collected"
        + (f" from {', '.join(reviewers)}" if reviewers else "")
    )
    console.print(
        theme.kv_table(
            [
                ("target", "--creatures", "mechas.accent"),
                (
                    "what",
                    "21 creature samples, five 1-5 readability questions each",
                    "mechas.value",
                ),
                ("who", "3 independent reviewers (63 rows total)", "mechas.value"),
                (
                    "progress",
                    progress,
                    "mechas.ok" if rows >= EXPECTED_ROWS else "mechas.warn",
                ),
            ]
        )
    )
    console.print()
    console.print("  [mechas.dim]try:[/]  [mechas.accent]mechas rate --creatures[/]")
    console.print(
        "  [mechas.dim]or: [/]  [mechas.accent]mechas rate --creatures --autoexport[/]"
        "  [mechas.dim](saves finished passes into the project by itself)[/]"
    )


def _show_status(console, root: Path, ratings_path: Path) -> None:
    console.print(theme.banner("rate — collection status"))
    rows, reviewers = _count_rows(ratings_path)
    style = "mechas.ok" if rows >= EXPECTED_ROWS else "mechas.warn"
    entries = [
        ("collected", f"{rows} of {EXPECTED_ROWS} rows", style),
        (
            "reviewers",
            ", ".join(reviewers) if reviewers else "none yet",
            "mechas.value",
        ),
        (
            "ratings file",
            str(ratings_path.relative_to(root)) if ratings_path.exists() else "not created yet",
            "mechas.path",
        ),
    ]
    gate_artifact = (
        root / "data" / "readability" / "slip_readability_calibration_gate_stage0.json"
    )
    if gate_artifact.exists():
        gate = json.loads(gate_artifact.read_text(encoding="utf-8"))
        ready = bool(gate.get("manual_readability_calibration_ready"))
        entries.append(
            (
                "calibration",
                "ready" if ready else "waiting for the full 63 rows",
                "mechas.ok" if ready else "mechas.warn",
            )
        )
    console.print(theme.kv_table(entries))
    if rows < EXPECTED_ROWS:
        console.print()
        console.print(
            theme.next_steps(
                [
                    "run [mechas.accent]mechas rate --creatures[/] and complete a pass",
                    "hand a pass each to two more reviewers",
                ]
            )
        )


def _ingest(console, root: Path, ratings_path: Path, source: Path) -> None:
    console.print(theme.banner("rate — ingest a downloaded ratings CSV"))
    if not source.exists():
        console.print(f"[mechas.err]Can't find[/] [mechas.path]{source}[/]")
        raise typer.Exit(code=1)
    first_line = source.read_text(encoding="utf-8").splitlines()[0].strip()
    if first_line != CSV_HEADER:
        console.print(
            "[mechas.err]That CSV's first line doesn't match the rating "
            "template,[/] so it isn't a rating export. Expected:\n"
            f"[mechas.dim]{CSV_HEADER}[/]"
        )
        raise typer.Exit(code=1)
    if ratings_path.exists():
        stamp = time.strftime("%Y%m%d-%H%M%S")
        backup = ratings_path.with_name(f"{ratings_path.stem}.{stamp}.bak.csv")
        shutil.copy2(ratings_path, backup)
        console.print(
            f"[mechas.dim]existing ratings backed up to[/] [mechas.path]{backup.name}[/]"
        )
    ratings_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, ratings_path)
    rows, reviewers = _count_rows(ratings_path)
    console.print(
        f"[mechas.ok]Saved[/] {rows} rows"
        + (f" from {', '.join(reviewers)}" if reviewers else "")
        + f" [mechas.dim]->[/] [mechas.path]{ratings_path.relative_to(root)}[/]"
    )
    _run_gate(console, root)


def _ensure_tool(console, root: Path) -> Path:
    tool_path = root / "data" / "readability" / TOOL_FILENAME
    if tool_path.exists():
        return tool_path
    console.print(
        "[mechas.warn]The rating page hasn't been generated yet[/] — "
        "building it now."
    )
    result = subprocess.run(
        [sys.executable, "-B", str(root / TOOL_BUILDER)],
        cwd=root,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0 or not tool_path.exists():
        console.print(
            "[mechas.err]Couldn't generate the rating page.[/] "
            "Details:\n" + (result.stderr or result.stdout)
        )
        raise typer.Exit(code=1)
    console.print("[mechas.ok]Rating page generated.[/]")
    return tool_path


def _run_session(
    console,
    root: Path,
    ratings_path: Path,
    *,
    port: int,
    autoexport: bool,
    open_browser: bool,
) -> None:
    console.print(theme.banner("rate --creatures — readability session"))
    _ensure_tool(console, root)

    exported = threading.Event()

    def on_export(rows: int, path: Path, backup: Path | None) -> None:
        exported.set()
        console.print()
        if backup is not None:
            console.print(
                f"  [mechas.dim]previous ratings backed up to[/] "
                f"[mechas.path]{backup.name}[/]"
            )
        marker = "mechas.ok" if rows >= EXPECTED_ROWS else "mechas.warn"
        console.print(
            f"  [{marker}]ratings saved[/] — {rows} of {EXPECTED_ROWS} rows "
            f"[mechas.dim]->[/] [mechas.path]{path.relative_to(root)}[/]"
        )
        if rows < EXPECTED_ROWS:
            console.print(
                "  [mechas.dim]keep the page open and add the next "
                "reviewer, or press Ctrl+C to finish for now[/]"
            )

    try:
        server = start_server(
            root / "data" / "readability",
            ratings_path,
            port=port,
            on_export=on_export,
        )
    except OSError:
        console.print(
            f"[mechas.err]Port {port} is busy.[/] Try "
            f"[mechas.accent]mechas rate --creatures --port 0[/] to pick a "
            "free one."
        )
        raise typer.Exit(code=1)

    actual_port = server.server_address[1]
    url = f"http://127.0.0.1:{actual_port}/{TOOL_FILENAME}"
    if autoexport:
        url += "?autoexport=1"

    rows, reviewers = _count_rows(ratings_path)
    console.print(
        theme.kv_table(
            [
                ("rating page", url, "mechas.path"),
                (
                    "autosave",
                    "on — finished passes save themselves"
                    if autoexport
                    else 'off — click "Save to project" on the finish screen',
                    "mechas.ok" if autoexport else "mechas.value",
                ),
                (
                    "collected so far",
                    f"{rows} of {EXPECTED_ROWS} rows"
                    + (f" ({', '.join(reviewers)})" if reviewers else ""),
                    "mechas.value",
                ),
            ]
        )
    )
    console.print()
    console.print(
        "  [mechas.dim]rate the 21 creatures in the browser — this window "
        "waits. Press Ctrl+C when you're done.[/]"
    )
    if open_browser:
        webbrowser.open(url)

    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass
    finally:
        server.shutdown()

    console.print()
    console.print("  [mechas.dim]session closed.[/]")
    rows, _ = _count_rows(ratings_path)
    if exported.is_set() or rows:
        _run_gate(console, root)
    else:
        console.print(
            "  [mechas.dim]no ratings were saved this session — run "
            "[/][mechas.accent]mechas rate --creatures[/][mechas.dim] "
            "anytime to continue.[/]"
        )


def _run_gate(console, root: Path) -> None:
    console.print()
    with console.status(
        "[mechas.dim]running the calibration gate...[/]", spinner="dots"
    ):
        result = subprocess.run(
            [sys.executable, "-B", str(root / GATE_SCRIPT)],
            cwd=root,
            capture_output=True,
            text=True,
        )
    if result.returncode != 0:
        console.print(
            "[mechas.err]The calibration gate hit an error:[/]\n"
            + (result.stderr or result.stdout)
        )
        raise typer.Exit(code=1)
    summary = {}
    try:
        summary = json.loads(result.stdout)
    except json.JSONDecodeError:
        pass

    collected = summary.get("ratings_collected")
    ready = summary.get("manual_readability_calibration_ready")
    rows_found = summary.get("rating_row_count", summary.get("completed_rating_rows"))
    entries: list[tuple[str, str, str]] = []
    if rows_found is not None:
        entries.append(("rows accepted", str(rows_found), "mechas.value"))
    entries.append(
        (
            "all ratings in",
            "yes" if collected else "not yet",
            "mechas.ok" if collected else "mechas.warn",
        )
    )
    entries.append(
        (
            "calibration",
            "READY — proxy scoring can now be graded against humans"
            if ready
            else "waiting on the remaining reviewer rows",
            "mechas.ok" if ready else "mechas.warn",
        )
    )
    console.print(theme.kv_table(entries))
    if ready:
        console.print()
        console.print(
            Text("the readability blocker is cleared — nice work.", style="mechas.ok")
        )
