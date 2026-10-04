"""The companion CLI front door for the local development cycle."""
from __future__ import annotations

import json
from pathlib import Path

import typer

from mechas_cli import development
from mechas_cli.workflows.rate import _workspace_python
from mechas_cli.workspace import find_workspace_root


def develop(
    start: str | None = typer.Option(None, '--start', help='Begin a preregistered slice; preserve unfinished state.'),
    advance: str | None = typer.Option(None, '--advance', help='Enter repair, enhance, or polish when its gates pass.'),
    note: str = typer.Option('', '--note', help='Concrete reason for the phase transition.'),
    verify: str | None = typer.Option(None, '--verify', help='Run focused or full verification with retained evidence.'),
    checkpoint: str | None = typer.Option(None, '--checkpoint', help='Record findings and the next action for resumption.'),
    status: bool = typer.Option(False, '--status', help='Show actual repository, phase, current checks and unmet remote gate.'),
    python: Path | None = typer.Option(None, '--python', exists=True, dir_okay=False, help='Use an already provisioned interpreter.'),
) -> None:
    """REVIEW -> REPAIR -> ENHANCE -> POLISH with resumable local evidence."""
    if sum((start is not None, advance is not None, verify is not None, checkpoint is not None, status)) > 1:
        raise typer.BadParameter('Choose one operation per invocation.')
    root = find_workspace_root()
    try:
        if start is not None:
            result = development.begin(root, start)
        elif advance is not None:
            result = development.advance(root, advance, note)
        elif verify is not None:
            result = development.verify(root, verify, str(python) if python else _workspace_python(root))
        elif checkpoint is not None:
            result = development.checkpoint(root, checkpoint)
        else:
            result = development.status(root)
        # The detailed inventories stay in evidence files; keep the command readable.
        visible = {k: v for k, v in result.items() if k not in ('initial_inventory', 'inventory')}
        typer.echo(json.dumps(visible, indent=2))
        if verify is not None and not result['passed']:
            raise typer.Exit(1)
    except development.WorkflowError as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(1)
