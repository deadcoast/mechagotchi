# The M7 Public Alpha — Reproduce Everything From This Document

Cycle 17 G6 (Phase G). Both builds — the ENGINE and the GAME — from a
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
uv sync --group lab --group cli --group game
```

## 1. Verify the whole workspace (the sweep)

One runner, the same locally and in CI (`.github/workflows/ci.yml`):

```powershell
uv run python -B tools/ci/run_sweep.py          # full (~4 min)
uv run python -B tools/ci/run_sweep.py --quick  # skips the 2-min workshop suite
```

Green means: 19 lab suites, the 295-test engine package, the
workshop, the CLI, the game suite, and JSON validation over every
committed data artifact.

## 2. Play the game (the second build)

```powershell
uv run python -B game/run_game.py        # or: mechas game --play
uv run python -B game/build_release.py   # the installable bundle -> game/dist/Mechagotchi/
```

Controls and the whole loop (companion → eras → covenant spending →
hatchery → contribute → review → repertoire/lineage → packs):
`game/README.md`. Weather key **4** selects REAL CuBFF weather (the
G2-ingested run; a checkout is required for the real forecast).
Quit and relaunch — the companion AND the campaign resume.

## 3. Regenerate the game's evidence (optional, deliberate)

```powershell
uv run python -B game/evidence.py   # 15 stage-0 artifacts under data/game_client/
```

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

- `docs/gap-analysis.md` (Phase G / M7), `research/experiment_reports/2026-07-12-phase-g-gate.md` (the gate this packet belongs to)
- `research/decision_records/0034-ci-and-zlib-conditional-pins.md`, `0035-pack-distribution-at-alpha.md`
- `tools/ci/run_sweep.py`, `.github/workflows/ci.yml`, `game/README.md`
