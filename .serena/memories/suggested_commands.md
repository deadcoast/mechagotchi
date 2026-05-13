# Suggested Commands

Use PowerShell from the repo root (`C:\Users\ryanf\github\_new\mechagotchi`). Prefer `rg` for searches.

Common inspection:
- `git status --short --branch --untracked-files=all`
- `rg --files`
- `rg -n "pattern" docs research data labs -g "*.md" -g "*.json" -g "*.py"`

Focused Python lab tests:
- `python -B -m unittest discover -s labs\workshop_editor -p "test_*.py"`
- `python -B -m unittest discover -s labs\slip_validator -p "test_*.py"`
- `python -B -m unittest discover -s labs\grid_genome -p "test_*.py"`
- `python -B -m unittest discover -s labs\lifecycle_sim -p "test_*.py"`
- `python -B -m unittest discover -s labs\map_elites_archive -p "test_*.py"`

Artifact validation:
- `python -m json.tool .\path\to\artifact.json`
- `node --check labs\workshop_editor\app.js`
- `Test-Path .\packages` (expected `False` until package work is explicitly started)
- `git diff --check` (may report pre-existing CRLF warnings; still check for new whitespace problems)

Example lab artifact commands are usually documented in the matching `research/experiment_reports/*.md` file.