# mechas-cli

`mechas` — the Mechagotchi companion CLI (Typer + Rich). The standard,
human-first surface for operating the workspace; created by decision
record 0007. A **supportive layer, not the application** — the application
is the Mechagotchi Computational Life Engine (root `README.md`).

- Command reference: `docs/cli/mechas-cli.md`
- Design charter (binding): `docs/cli/mechas-cli-design.md`

Install from the repository root:

```powershell
uv tool install --editable .\tools\mechas_cli
mechas --help
```

Tests (stdlib parts always run; Typer-surface tests skip unless the `cli`
dependency group is provisioned):

```powershell
python -B -m unittest discover -s tools/mechas_cli/tests -p "test_*.py"
uv sync --group cli
.venv\Scripts\python -B -m unittest discover -s tools/mechas_cli/tests -p "test_*.py"
```
