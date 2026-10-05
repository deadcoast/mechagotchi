# The M7 Public Alpha — Reproduce Everything From This Document

Established in cycle 17 G6 (Phase G); launch guidance refreshed through Cycle 33 W1,
2026-10-05. Both builds — the ENGINE and the GAME — from a
fresh clone, on the repo's own evidence discipline. Every claim below
is backed by a retained artifact or a test suite; current recovery changes
remain uncommitted for the user. Nothing is
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
is 2,656 tests and 2,294 JSON artifacts (W1 full run
`20261005T115738-611ddb0c`); two named DR 0034 pins skip on zlib 1.3.1.
All 24 suites passed without source mutations. Runtime depends on the machine.
The historical Q4 gate was 2,493 tests / 2,269 JSON artifacts.

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
`game/dist/w1-import-inboxes-final/Mechagotchi/Mechagotchi.exe`; keep `_internal` beside it.
From the repository root, launch with an explicit save directory. An absolute
executable path also works from another cwd:

```powershell
.\game\dist\w1-import-inboxes-final\Mechagotchi\Mechagotchi.exe --keeper-dir "$env:USERPROFILE\.mechagotchi"
```

Without an explicit directory, the current native build starts new saves in
`~/.mechagotchi`. Existing `_internal/keeper` lives continue in place when no
user-home save exists; when both exist, the user-home save wins and the legacy
bytes remain untouched. No migration is performed. Add `--learning-policy qtable`
with `--new` and a separate save home to try experimental learning; resume keeps
that choice. The incumbent remains the default after the R3 comparability refusal.
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
Quit and relaunch — the companion AND the campaign resume. Interactive E keeps
the casing responsive with real progress while care pauses; Escape cancels
uncommitted work, and close waits for cancellation or completed-result saving.
Cold model loading cancels at its next boundary. See the T5 responsiveness report
for the original responsiveness investigation. U1 preserves those scientific
results while recording the actual final-best evaluation, with measured 96/384
evaluations. V reads saved original footage from care/T or its matching B elite;
other selections say not recorded. Legacy footage keeps its original label.
Read `research/experiment_reports/2026-10-04-original-era-recordings.md` for
current measurements, bounded retention and interrupted-recording recovery.

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
- Import a pack: copy `data/packs/mechagotchi_starter_pack.json` into
  `<save directory>/packs/`, press **K**, select it and press **Enter**.
- Press **I** to select a staged covenant and **Enter** to apply it to future
  eras/hatches/adoptions. The current companion keeps its covenant and policy.
  Close the picker before **W** gathers staged creatures for **E**; each still
  faces engine admission. **F1** explains the active inbox and **F5** refreshes
  changed files. Existing filenames work without renaming.

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
CLI and native launch checks. Cycle 28's implemented learning option, measured
default refusal and native save-home repair are recorded in
`research/experiment_reports/2026-10-04-playable-learning.md`; consult the live
runner for its final full gate and the live queue for the bounded next action.

Cycle 31 U1 closes original final-best evaluation capture and saved playback.
Its report, DR 0074, immutable observation/sample artifacts and
`.development/u1-live-handoff.json` identify its then-current local build and restart.
The full gate is local; native keyboard, maximum-scale observations and
exact-published-SHA Windows/Ubuntu Actions remain outside the verified claims.

Cycle 32 V1 adds N in B for exact saved niche occurrences and Ctrl+[ / Ctrl+]
in T for recorded predecessor campaigns. T/V/A retain the selected historical
context and current-covenant adoption; missing history is explicit and care is
paused. This is recorded-fact navigation, with no E5/family or founder inference.
Read `research/experiment_reports/2026-10-04-niche-history.md` and
`.development/v1-live-handoff.json` for its then-current build, evidence and restart.

Cycle 33 W1 connects named packs and covenant inboxes with paused previews,
explicit Enter, stale-file checks, safe per-item staging and contextual help.
The latest local build is `game/dist/w1-import-inboxes-final/Mechagotchi/Mechagotchi.exe`
with adjacent `_internal`. Read `research/experiment_reports/2026-10-05-import-inboxes.md`
and `.development/w1-live-handoff.json` for exact source/native evidence and restart.
This local closure does not claim native keyboard, maximum inbox scale or
published-SHA CI verification.
