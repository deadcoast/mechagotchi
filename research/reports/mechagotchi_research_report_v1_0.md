# Mechagotchi Research Report v1.0

Date: 2026-07-07

## Executive Summary

The realization wave — the version number is earned, not incremented.
Between v0.10 (2026-07-05) and this report, the repository executed its
own North Star (decision record 0017: the ENGINE+GAME duality, deep
integrations over breadth) from a six-module engine with no game to a
**ten-module engine whose showcase game is live end to end**, across
five completed development cycles (02–06, archived under
`audits/complete/`).

**Engine arc — the module program is finished.** `runtime` (DR 0008)
composed the six research modules into `live_cycle` + `evolve`;
`learning` (DR 0009) promoted the feedback switchboard under its
honestly bounded claim; `storage` (DR 0022, gates proven lab-first in
`campaign_store`) landed the SQLite campaign ledger; and `slip`
(DR 0027) collapsed four behaviorally-identical private mirrors into
the tenth module after a five-way reconciliation measured zero
divergences. `render` is dispositioned, not promoted (DR 0026:
REJECTED-until-consumer with its re-opener named — the packet contract
already ships in `genome`). The SLIP schema ladder completed every rung
(forbidden_traits through deliberation; the zoo gates 18/20 archetypes
with zero unplanned gaps), packet v2 carries animation and the
species' visual grammar, and two latent defects were found by building
the game on the engine and fixed RED-first: the aligned-but-invalid
promotion drift (the lab's T1 validity gate had never reached
`runtime.live_cycle`) and, later, the boundary it guarded was measured
outright — a damage-scaled MORTALITY GRADIENT (0.025 at the mildest
regime to 0.10 at the harshest, cause-diagnosed to the disconnected
body core), with the skip retained as correct biology and the
connected-core repair contract explicitly rejected.

**Game arc — "Eras of the Soup" ships whole.** DR 0021 fixed the
design (era = one `evolve` run; campaign = the era chain through
`founder_grids`; first law: everything shown is engine truth) and every
step of its core loop is now live at a real surface: Review (per-era
recorded replays, the DR 0023 scrubber), Covenant (unlock facts SPEND —
palettes, deliberation depth on the authority's real floor, cap
doubling, the earned parenting blend), Contribute (released workshop
creatures found the next era through the engine's own gates),
weather (CuBFF pressure sources — storm 1.17x vs stable 0.90x measured
at the same seed; real-export ingest closed as an OPTIONAL seam by
owner decision, cycle 04), and Collect (unlock facts citing resolvable
report metrics). All five DR 0021 player-notices were audited end to
end (E5) and are **five of five live** — the last one (creatures
visibly think) closed by threading the R1 deliberation record into
episode history so the scrubber renders the thought. The mortal-wound
gradient is a felt phenomenon ("the toll"), extinction seats successors
carrying only their unlocks, and a 12-era soak proved the whole
persistence spine (ledger round-trips, deterministic replay of every
stored era, replay-hash matching, founder/unlock chain continuity) at
campaign scale.

**ML/data arc — the fuel was built, burned, and improved the model.**
The og dataset table completed (mechaseed_200, mutationbench_5000
signature-verifiable, replay_100k_ticks byte-deterministic gzip), then
its consumers returned two findings: the R3 learned-readability model
GENERALIZES to real mutations (0.9406 pairwise on 2,880 physics-labeled
real pairs), and the replay corpus produced a textbook survivorship-bias
catch (the naive per-lived-tick mean ranked the switchboard LAST; the
engine's own full-horizon statistic flips it — switchboard 0.789 at
survival 1.00 vs idle 0.121 at survival 0.00). The fine-tune experiment
then augmented the ranker with the real pairs and won every gate
(cross-parent real heldout 0.98018 → 1.0, zero synthetic regression,
live physics not worse) — the adopted weights are a committed,
auditable artifact the session loads. The manual rating system remains
the fallback and calibration check throughout, its evidence state
honestly 0 of 63 rows by standing owner decision.

Test base: 747 at v0.10 → **1,210 all green** (847 lab across 16 labs +
290 package + 52 workshop + 21 CLI). Promotion gate: **9
promotion-ready of 10 candidates** (the tenth is the honestly-blocked
manual-ratings gate). The tracked-bytecode hazard is closed (144 files
untracked, cycle 07 V3).

This report consolidates and links the underlying experiment reports;
it does not replace them.

## Consolidated Reports (46) and Decision Records (20)

The window (2026-07-05 post-v0.10 → 2026-07-07) is ledgered in full in
`research/README.md`; the cycle queues are archived at
`audits/complete/01`–`06`. Highlights by arc (every path in the
manifest's `referenced_artifacts`):

- **Module promotions**: runtime (`2026-07-05-mecha-engine-runtime-promotion.md`),
  learning (`...-learning-promotion.md`), storage
  (`2026-07-07-campaign-store.md`, `...-storage-module-promotion.md`),
  slip (`2026-07-07-slip-module-promotion.md`); dispositions DR 0024
  (grid animation/species), DR 0026 (render), DR 0027 (slip).
- **The game loop**: DR 0017 (the recalibration), DR 0021 (the design),
  `2026-07-07-game-loop-session-runner.md` (G2 + the promotion-drift
  fix), `...-keeper-session-surface.md` (G4),
  `...-covenant-step.md` (C4), `...-per-era-replay.md` (C5),
  `...-replay-recorder.md` (R5/DR 0023),
  `...-mortal-wound-signal.md` (D2), `...-five-notices-audit.md` (E5),
  `...-seen-thought.md` (F1), `...-campaign-scale-soak.md` (D5).
- **The living dynamics**: `2026-07-06-ctm-deliberation-live.md` (R1),
  `...-cubff-live-lineage-pressure.md` (R2, + DR 0020 promotion),
  `...-learned-readability.md` (R3, + DR 0025 promotion,
  `2026-07-07-readability-selection-promotion.md`),
  `2026-07-07-repair-validity-boundary.md` (C6).
- **Data and ML**: `2026-07-07-dataset-program.md` (R6),
  `...-dataset-consumers.md` (E3), `...-real-mutation-finetune.md` (F3).
- **The ladder and stress work** (cycle-01 tail):
  the five slip-ladder rung reports, `...-slip-v2-packet-v2-port.md`,
  `...-stress-regime-evolution.md`, `...-stress-learning-benchmark.md`,
  `...-workshop-engine-wire.md`, `2026-07-06-slip-ladder-gates.md`.

## Headline Metrics

| Metric | Value |
| --- | --- |
| Promoted `mecha_engine` modules | **10 of 10 og targets** (render dispositioned with a named re-opener) |
| Promotion gate | 9 promotion-ready of 10 candidates (manual-ratings gate honestly blocked) |
| DR 0021 player-notices live | **5 of 5** |
| CuBFF weather directionality | storm 1.17x vs stable 0.90x damage at the same seed |
| Learned readability (adopted, real-augmented) | cross-parent real heldout 0.98018 → **1.0**; zero synthetic regression |
| Real-mutation generalization (pre-fine-tune) | 0.9406 pairwise / 2,880 physics-labeled pairs |
| Replay corpus verdict | switchboard 0.789 episode need-balance at survival 1.00 vs idle 0.121 at 0.00 (100,004 ticks, zero simulation) |
| Mortal-wound gradient | 0.025 (mildest) → 0.10 (harshest); ~0.0125 in the session band; skip retained as biology |
| Campaign soak | 12 eras, spine all-green: ledger round-trips, deterministic replay of EVERY stored era, hash-matched replays, continuous chains |
| Test base | 747 → **1,210 all green** |

## Deliberately Open (next_sequence)

- **Owner decisions, not tasks**: the repo-wide license grant; the
  `[project]` dependencies policy (deliberately blocked); manual
  readability calibration (pipeline ready, 0/63 rows by choice);
  real-CuBFF export ingest (an optional drop-in seam — the synthetic
  weather is the shipped answer, cycle 04).
- **Named re-openers, not queued work**: a `mecha_engine.render`
  drawing module (the moment a non-workshop Python consumer needs to
  rasterize — DR 0026); the repair model's core-preservation as a
  difficulty tuning lever (only if the mortal-wound rate is ever judged
  too high — C6); mixed-species soups re-opening grid-level
  species_class (DR 0024).
- **Cycle 07's remainder**: V2, the `docs/agent-standards.md` refresh.

## Sources

- `research/README.md` (the master ledger; every triad in the window)
- `audits/complete/01/`–`audits/complete/06/` (the archived cycle queues)
- `research/decision_records/0008`–`0027` (the window's twenty records)
- `docs/project-research/research.md` (the governing plan)
- `research/reports/mechagotchi_research_report_v0_10.md` (the prior consolidation)
- `data/package_promotion/mecha_engine_package_promotion_gate_stage0.json` (the gate's machine-readable truth)
