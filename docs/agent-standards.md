# Agent Onboarding — Mechagotchi

Written 2026-07-04; refreshed 2026-07-07 (cycle 07 V2, report v1.0) for
the next Fable 5 session. This file orients you; it does not replace the
living documents. **State described here may be stale — re-verify
against `git log` and the gate artifacts before relying on it.**

## 1. What this project is

A grid-based artificial-life companion platform, built research-first:
the **Mechagotchi Computational Life Engine** (`packages/mecha_engine`,
ten promoted modules) and its showcase game **"Eras of the Soup"**
(decision record 0021 — the Keeper stewards a bloodline through eras of
a computational-life soup), plus the **mecha_workshop** authoring layer
(grid editor, SLIP creator, preview/scrubber, inspector, Keeper session
page) and the **mechas** companion CLI. SLIP = Synthetic Learning
Intelligence Profile, the user-authored covenant that governs
generation and behavior (`research/glossary.md`).

The defining property of this repo: **the documentation is the
deliverable and the governance.** Nothing is claimed without executable
evidence; nothing is promoted without passing a documented gate. The
game's first law (DR 0021): everything shown to the player is engine
truth — a report field, an artifact, a recorded replay.

**Standing identity constraint (anti-drift — root `README.md`): this
repository is NOT a CLI application.** The `mechas` CLI (`tools/`) is a
supportive layer only. The application is the engine, inspired by the
CuBFF study behind *Computational Life* (arXiv:2406.19108, local copy
`assets/pdf/2406.19108v2.pdf`). No supporting surface may quietly
become the project. MIVIM.dev flagship — hold every change to the
established standards.

## 2. The prime directive

**Seek knowledge locally first, from the documents, for every
request.** Working from memory instead of the repo's own documents
causes drift — the one failure mode this system is designed to prevent.

Authoritative chain, in order:
1. `docs/project-research/research.md` — the governing plan; DR 0017
   (`research/decision_records/0017-...md`) is the North Star: the
   ENGINE+GAME duality, deep integrations over breadth.
2. `research/decision_records/0001–0027+` — ADRs; check for newer ones.
3. `research/package_specs/*` — package contracts, gates, the
   **contract traceability matrix**.
4. `research/README.md` — the master traceability ledger (triads).
5. `data/**/**_stage0.json` — gate artifacts = machine-readable truth.
6. `research/reports/` — consolidated waves; **v1.0 is the newest**
   (the realization wave); read its manifest's `next_sequence`.

When docs conflict: the more specific gate/spec wins; decision records
win over plans; executed artifacts win over prose claims.

## 3. State snapshot (2026-07-07, report v1.0)

- **The module program is FINISHED.** Ten promoted modules with
  contract tests + lab-parity pins: `genome`, `generation`,
  `lifecycle`, `archive`, `provenance`, `repair` (DR 0006), `runtime`
  (DR 0008: `live_cycle` + `evolve`, with `founder_grids`,
  `cubff_pressure_source`, `readability_selection`, `record_frames`
  seams), `learning` (DR 0009, bounded wellbeing claim), `storage`
  (DR 0022: the SQLite campaign ledger), `slip` (DR 0027: the single
  SLIP authority; four private mirrors collapsed). `render` is
  DISPOSITIONED, not promoted (DR 0026: REJECTED-until-consumer — the
  packet contract ships in `genome`; re-opener: a non-workshop Python
  rasterizer consumer). Gate: 9 promotion-ready of 10 candidates (the
  manual-ratings gate is honestly blocked by owner deferral).
- **The game is live end to end.** All five DR 0021 player-notices
  (E5 audit + F1): weather with provenance, creatures SEEN thinking
  (deliberation rides episode history to the scrubber), legibility on
  every era card (honest direction: it drifts DOWN across chained eras
  at Stage-0 scale), released creatures founding eras (the Contribute
  step), and persistence + per-era recorded replays. The Covenant step
  SPENDS unlock facts; extinction seats successors carrying only
  unlocks; mortal wounds ("the toll") read from `archive_decision`.
  Play state lives in `data/game_loop/keeper/` (gitignored; a live
  game is not evidence). Surfaces: `mechas session
  --open/--era/--status/--new`, the `/session` page, the preview
  scrubber.
- **The ML track**: og datasets delivered AND consumed
  (`data/datasets/`); the ADOPTED readability model is a committed
  auditable artifact (`data/readability_benchmark/
  adopted_readability_model.json` — real-mutation-augmented, all F3
  gates green); the manual rating system stays the FALLBACK, its state
  honestly 0/63 rows by standing owner decision.
- **Tests**: **1,210 all green** (847 lab across 16 labs + 290 package
  + 52 workshop + 21 CLI). Run the sweep for exact current counts.
- **Cycles**: 01–06 archived complete under `audits/complete/`;
  `audits/TODO.md` is the active queue (cycle 07: V1 ✓, V2 = this
  refresh, V3 ✓).
- **Owner decisions on record (NOT tasks)**: real-CuBFF export ingest
  is an OPTIONAL drop-in seam (cycle 04 — synthetic weather is the
  shipped answer; nothing external is required); the `[project]`
  dependencies policy stays deliberately blocked; the repo-wide
  license grant stays pending; manual calibration deferred.

## 4. The document development format (non-negotiable)

Documents are living files: **every code or data change updates its
documents in the same change.**

- **Triad convention**: each finding = dated experiment report
  (`research/experiment_reports/YYYY-MM-DD-kebab-slug.md`) + algorithm
  card (`snake_case`, same stem) + lab code +
  `data/<lab>/<slug>_stage0.json` — all ledgered in
  `research/README.md`.
- Experiment reports carry **RED/GREEN verification blocks** with exact
  commands and pasted output, and a `## Sources` footer of repo paths.
- Artifacts carry `status` / `closed_states` / `blocked_states` /
  `decision`. Keep blocked states explicit; never silently drop one.
- Consolidated reports (v0_N/v1_N + manifest) group waves; they link,
  never replace. Every manifest path must resolve — verify before
  writing.
- Completion checklist (also in CLAUDE.md): run the changed lab's tests
  → validate changed JSON with `python -m json.tool` → update triad
  docs → sweep for stale blocker wording.
- **The cycle rule**: a task is complete when developed to its
  description, then marked in `audits/TODO.md`. Development proceeds
  continuously; planning triggers ONLY when the TODO is exhausted and
  confirmed COMPLETE (full sweep green) — then archive to
  `audits/complete/NN/` and plan the next cycle from the seams the
  finished cycle recorded.

## 5. Honesty norms (learned and enforced across cycles)

- **Gates derive from evidence, never constants.** A probe that cannot
  fail is a bug. If a gate would flip on weak evidence, harden its
  derivation instead.
- **Record negative results and refuted hypotheses.** C6's
  "extreme-damage-only" hypothesis was REFUTED by its own measurement
  (the mortality gradient) — and the refutation is the finding.
- **Beware the statistic, not just the data.** E3's survivorship-bias
  catch: the naive per-lived-tick mean ranked the switchboard LAST; the
  engine's own full-horizon rule flipped it. When comparing outcomes,
  reconstruct the engine's exact statistic.
- **A faithful replay reproduces the original INPUTS exactly.** D5's
  two harness bugs: the C4 earned blend must be replayed (not
  defaulted), and `founder_grids=None` ≠ `[]` (an intentional DR 0016
  distinction). The engine's input distinctions are real.
- **Never pin environment observations in tests** (H-01): assert the
  policy/decision; record availability as per-run observations. Pin
  the test harness's capture environment (ambient `FORCE_COLOR` broke
  plain-substring assertions once).
- **Parity before promotion; additive seams byte-identical off.**
  Package ports keep lab semantics verbatim (error strings included),
  pinned lab-side over full fixture corpora. New engine keywords
  default to byte-identical (the `founder_grids`/`record_frames`/
  `readability_selection` pattern). Watch for promotion DRIFT: the
  aligned-but-invalid crash happened because a lab improvement never
  reached the promoted mirror — and no pinned seed exercised the path.
- **Regenerate artifacts you invalidate**, and explain each delta.
  Never let a live surface overwrite committed evidence (play state is
  gitignored for exactly this reason).

## 6. Working cadence that worked

- Work the active `audits/TODO.md` queue task-by-task; one commit per
  completed task naming the task ID, evidence, and doc updates.
- RED-first for engine changes; probe empirically before designing
  (the boundary scans, the reconciliation sweeps).
- Delegate wide surveys to read-only sub-agents with spec-first briefs;
  keep verification, triad docs, gate reruns, and commits in the
  orchestrator.
- Rerun the **full sweep** (16 labs + package + workshop + CLI) before
  claiming a cycle complete; suites are fast.

## 7. Environment and commands

```powershell
# One lab suite (stdlib unittest; no pytest; run from anywhere)
python -B -m unittest discover -s labs/grid_genome -p "test_*.py"
# Package suite
python -B -m unittest discover -s packages/mecha_engine/tests -p "test_*.py"
# Promotion gate (candidate statuses are the machine truth)
python -B labs/package_promotion/package_promotion_gate.py
# Validate changed JSON
python -m json.tool data/<path>.json
# Play surfaces
mechas session --open        # the Keeper page
mechas workshop --preview    # packets, live_cycle, replays
```

- `python` resolves to system CPython 3.14; user site-packages leak in
  (hence H-01). Lab extras (`pydantic`, `jsonschema`) via
  `uv sync --group lab` (DR 0005). All package modules stdlib-only;
  the **package** dependency policy is deliberately blocked.
- `-B` always — tree hygiene (the old tracked-bytecode hazard was
  CLOSED in cycle 07 V3; the ignore rule holds).
- Git: LF→CRLF warnings are normal noise. Commit messages end with the
  Claude co-author line. Push per the owner's direction.
- Package tests reach `mecha_engine` via a subprocess with PYTHONPATH
  at `packages/mecha_engine/src`; no `sys.path` text anywhere in the
  package tree (the boundary scan greps for it). Package code/tests
  import `mecha_engine`, never `labs`; labs may import the package
  (that is how parity pins work). The workshop layer may import both.

## 8. Traps

- The grid validator enforces the full schema surface — including the
  64-char `grid_id` cap. Reassign ids per cycle (`live_cycle` does);
  suffix accumulation overflows (this trap has bitten TWICE, most
  recently a study harness measuring its own bug as biology).
- `founder_grids=None` (no wire) ≠ `[]` (wire ran, admitted nobody) —
  reports differ by a whole block. Same class of trap: rung-conditional
  keys exist only when their feature ran.
- The lifecycle sim is bistable (stress ≤0.94 stabilizes, ≥0.95
  collapses ~tick 12–14); survival variance needs the morphology
  stress probe. Idle creatures starve by ~tick 11 — mind survivorship
  bias in any per-tick aggregate.
- `deliberation.max_ticks` has an authority floor of 2 (a "+1 per
  tier" design must ride the real schema floor).
- The user's explicit authorization is required for scope-expanding
  steps the decision records gate (license decisions, publishing,
  anything the owner-decision ledger names). When a doc says "only
  when the user explicitly starts X" — ask, with a recommendation.

## 9. First moves for a fresh session

1. `git log --oneline -15` — what happened since this file was
   refreshed.
2. Read `research/reports/mechagotchi_research_report_v1_0.md` (or
   newer) and its manifest's `next_sequence`.
3. `audits/TODO.md` — the active cycle queue; work it continuously.
4. `python -B labs/package_promotion/package_promotion_gate.py` —
   candidate statuses are the truth, not this file.
5. Owner-decision items (license, dependencies, calibration, CuBFF
   ingest) are NOT tasks — leave them unless the owner speaks.
