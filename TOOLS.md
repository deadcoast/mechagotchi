# TOOLS.md
<!--
> NOTE:
> - This file provides quick access to cheat sheet style notes on tool usage.
> - This file is NOT for documenting exposition or large details.
-->
---

## mechas — companion CLI

Docs: `docs/cli/mechas-cli.md` (reference) · `mechas-cli-design.md` (charter) · `mechas-cli-audit.md` (status)

### Install (one time, from repo root)

```powershell
uv tool install --editable .\tools\mechas_cli   # global `mechas` command
uv sync --group lab --group cli                 # dev venv (BOTH groups — uv sync is exact)
```

### Commands

```powershell
mechas --help                                # command overview
mechas --version                             # CLI version
mechas status                                # workspace at a glance (modules, gates)

mechas rate                                  # list rating targets + examples
mechas rate --creatures                      # full rating session: serve + browser + save + gate
mechas rate --creatures --autoexport         # same, finished passes save themselves
mechas rate --creatures --port <n>           # fixed port (default: auto-pick a free one)
mechas rate --creatures --no-browser         # don't auto-open the browser
mechas rate --status                         # rows collected (of 63), reviewers, readiness
mechas rate --ingest <file.csv>              # bring a downloaded ratings CSV in + run gate

mechas workshop                              # list workshop targets
mechas workshop --editor                     # grid editor: draw, live engine validation, save
```

### Notes

- Rating session: rate in the browser, Ctrl+C in the terminal when done — the calibration gate runs automatically.
- Overwrites are always backed up (`*.bak.csv`, gitignored).
- Works from any directory; `MECHAGOTCHI_ROOT` overrides workspace detection.

### CLI tests

```powershell
.venv\Scripts\python -B -m unittest discover -s tools/mechas_cli/tests -p "test_*.py"
```
