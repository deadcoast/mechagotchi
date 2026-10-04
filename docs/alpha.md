# The M7 Public Alpha — Reproduce Everything From This Document

Established in cycle 17 G6 (Phase G); launch guidance refreshed at Q5,
2026-10-04. Both builds — the ENGINE and the GAME — from a
fresh clone, on the repo's own evidence discipline. Every claim below
is backed by a committed stage-0 artifact or a test suite; nothing is
asserted without a gate.

## 0. Prerequisites

- **Python 3.13+** (the byte-identity fixture pins additionally want
  the zlib-ng CPython build family — Windows CPython 3.14; under any
  other build those two pins SKIP with a named reason and every
  content gate still runs — decision record 0034).
- **[uv](https://docs.astral.sh/uv/)** (dependency groups + the venv).

```powershell
uv sync --locked --group lab --group cli --group game
```

For a fresh checkout, the command above provisions dependencies. For this
already provisioned Windows checkout, keep its existing Python 3.13.9 environment;
all commands below reuse `.venv/Scripts/python.exe`. On Unix the interpreter
path is `.venv/bin/python`. No environment replacement is needed for play/tests.

## 1. Verify the whole workspace (the sweep)

One runner, the same locally and in CI (`.github/workflows/ci.yml`):

```powershell
.venv/Scripts/python.exe -B tools/ci/run_sweep.py          # full, all 24 suites
.venv/Scripts/python.exe -B tools/ci/run_sweep.py --quick  # local diagnosis, not a full gate
```

A full gate covers 19 lab suites plus package, CLI, game, workshop and CI-runner
suites, with JSON validation over every data artifact. Current verified scope
is 2,493 tests and 2,269 JSON artifacts; two named DR 0034 pins skip on zlib 1.3.1.
Runtime depends on the machine (the observed Q4 full run took about 9m24s).

## 2. Play the game (the second build)

```powershell
.venv/Scripts/python.exe -B game/run_game.py
.venv/Scripts/python.exe -B game/run_game.py --new --keeper-dir keeper/example
.venv/Scripts/python.exe -B game/run_game.py --keeper-dir keeper/example
.venv/Scripts/python.exe -B game/build_release.py --windowed # -> game/dist/Mechagotchi/
```

New companions use the measured cleanliness covenant. **G** cleans only when
the companion's covenant supports it; existing saves retain their covenant.
**F1** shows all controls and pauses care, **PgUp/PgDn** or the wheel browse
long casing text, and **Escape** closes help before quitting. Only the keeper
feeds; the companion's autonomous feed decision is a beg. No Q-table default
promotion has occurred.

The supportive CLI can also launch from this source checkout:

```powershell
$env:PYTHONPATH = (Resolve-Path tools/mechas_cli/src).Path
.venv/Scripts/python.exe -B -m mechas_cli.app game --play --new --keeper-dir keeper/cli-example
.venv/Scripts/python.exe -B -m mechas_cli.app game --play --keeper-dir keeper/cli-example
```

A covenant option selects a new life, never replaces an existing save silently:

```powershell
.venv/Scripts/python.exe -B game/run_game.py --new --slip data/slips/valid/slip_lcd_seed.json --keeper-dir keeper/incumbent-example
```

A new campaign inherits that companion's covenant; a resumed campaign retains
its saved covenant. The demonstrated local Windows bundle is
`game/dist/q4-controls/Mechagotchi/Mechagotchi.exe`; keep `_internal` beside it.
Launch it from any cwd; it uses bundled inputs and its player save home.
This is an unsigned local one-folder build, not hosted distribution or proof of
remote CI. The `mechagotchi` console entry point belongs to an installed game
package; it is not present in this dependency-only workspace.

Controls and the whole loop (companion → eras → covenant spending →
hatchery → contribute → review → repertoire/lineage → packs):
`game/README.md`. Weather key **4** selects REAL CuBFF weather (the
G2-ingested run; a checkout is required for the real forecast); key
**5** selects the callback forecast — the first weather whose
harshness channels are LIT, sourced from the committed I3 callback
records (decision record 0043).
Quit and relaunch — the companion AND the campaign resume.

## 3. Regenerate the game's evidence (optional, deliberate)

```powershell
.venv/Scripts/python.exe -B game/evidence.py   # 16 stage-0 artifacts under data/game_client/
```

The historical evidence builders retain explicit HELLO_SLIP bindings and
answer their original questions; this command does not measure the new default.
Do not migrate an old measurement onto a new definition or casually overwrite
committed evidence. New questions get new artifacts and records.

Evidence regeneration is a deliberate act, not a CI job (the G1
report records this decision): CI verifies the suites per push; the
artifacts are committed measurements.

## 4. Share (the alpha's community loop, DR 0035)

Packs travel as FILES; the engine's gates — never trust — judge their
contents (build refuses invalid, import re-judges and stages, era
admission judges again at run):

- Export your covenant: **X** in the client → `keeper/covenants/`.
- Import a pack: put it at `keeper/packs/pack_import.json`, press
  **K**. The committed example:
  `data/packs/mechagotchi_starter_pack.json`.

## 5. Reproduce the real CuBFF corpus (optional; Linux/WSL)

The committed corpus (`data/cubff_real_ingest/source_snapshots/`) came
from one genuine upstream run; its README records the exact commit,
build (`make CUDA=0`), and parameters. The 400-state transducer study
(`data/cubff_transducer/real_transducer_study_stage0.json`) records
its full protocol and per-state results.

## 6. Where the truth lives

- `docs/gap-analysis.md` — the roadmap this alpha completes.
- `research/README.md` — the master traceability ledger (every
  finding: report + card/DR + lab + data).
- `research/experiment_reports/` — dated reports with RED/GREEN
  verification blocks; `research/decision_records/` — the ADRs.
- `data/` — the evidence artifacts the ledger cites.

## Sources

- `docs/gap-analysis.md` (Phase G / M7 — RETIRED per its own charter; the measured history), `research/experiment_reports/2026-07-12-phase-g-gate.md` (the gate this packet belongs to)
- `research/experiment_reports/2026-07-21-callback-forecast.md` + `research/decision_records/0043-callback-forecast-adoption.md` (forecast key 5 and the sixteenth game artifact), `research/experiment_reports/2026-07-26-phase-k-gate.md` (the freshness pass that corrected the artifact count)
- `research/decision_records/0034-ci-and-zlib-conditional-pins.md`, `0035-pack-distribution-at-alpha.md`
- `tools/ci/run_sweep.py`, `.github/workflows/ci.yml`, `game/README.md`

## Current consolidation

`research/experiment_reports/2026-10-04-phase-q-gate.md` records actual source,
CLI and native launch checks. Cycle 27 is archived; cycle 28 is planned in
`docs/development/cycle-28-learning-consumer.md` and has not started.
