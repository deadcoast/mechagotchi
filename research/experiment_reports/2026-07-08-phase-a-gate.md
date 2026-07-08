# Experiment Report: The Phase-A Gate — the 16×16 Foundation (Cycle 09 · ENGINE · A5)

Date: 2026-07-08

## WHY

`docs/gap-analysis.md` names the foundational gap: everything ever
proven in this repository was proven at 8×8 with ~13-cell bodies, while
the documents name 16×16 as the primary scale — MVP 0.1's own target,
the creature that "proves the entire thesis" (validity-research §1.34).
Phase A's charter: move the foundation to documented scale so every
downstream phase builds on real ground. This is the consolidated gate
report over cycle 09 tasks A1–A4.

## THE GATE, surface by surface

| Surface | Ratified / measured at 16×16 | Evidence |
| --- | --- | --- |
| **Invariants** (A1) | Body-core floor 18 via `max(4, 18·w·h//256)` (reproduces 8×8's 4 exactly); 8-neighbor topology reaffirmed (26% of seed cores diagonal-dependent); chance-pass rejection 0.625% → 0/4,000 at scale; candidates {4, 8, 24} refuted, 18 preferred over 16 by the p95=17 noise blob | `2026-07-08-16x16-invariant-scaling.md`, DR 0029 |
| **Corpus** (A2) | 50 hand-authored creatures (core 18–85, median 51.5; ten per palette; profile-view asymmetrics, limbless forms, sensor pairs, single anchors; NOT upscaled blobs) + 200 invalid counterexamples + the size-parametric workshop canvas | `2026-07-08-16x16-seed-corpus.md` |
| **Validator** (A3) | The floor law enforced in lab + package with byte-identical 8×8 outcomes; the 16×16 corpora joined the 500-file parity pin (error-string equality) | `2026-07-08-16x16-validator-generation.md` |
| **Generation** (A3) | Size-parametric training (mixed sizes fail loudly); 25/25 valid candidates over the floor at [16,16] in lab + contract gates; validity 100% by the stabilizer's construction at both scales | same report |
| **Stress probe / lifecycle** (A3) | The `/16` denominator measured as a TOTAL 16×16 collapse and re-derived from evidence: `mass/(w·h/4)` adopted into the engine and four mirrors; real 16×16 episodes measured; `initial_state` verified dimensionless | `2026-07-08-stress-probe-scaling.md` |
| **Repair** (A3) | Size-parametric feature layout (8×8 weights bit-for-bit); 40/40 valid guarded held-out repairs; 89.4% exact-token restoration; the NumPy trigger measured and NOT fired (21 s stdlib full-corpus training) | `2026-07-08-repair-at-16x16.md` |
| **SLIP** (A3) | Mass bounds reference-canvas-scaled (DR 0030) — the 2,080-case pair pin unmodified; the corpus aligns with the shipped zoo | `2026-07-08-slip-size-relative-bounds.md` |
| **Archive** (A4) | Body-mass bins re-derived (`edge·w·h//64`); the mass axis spreads ≥4 of 5 bins instead of collapsing | commit `84cd2be` |
| **Evolution + game surfaces** (A4) | Session defaults raised to 6×16 on measurement (1.2 s/era; curve to 10×32 = 4.9 s recorded); unlock tiers re-tuned to measured magnitudes; size-coherent eras with gate-rejected wrong-scale founders; scale-aware campaign continuity; the workshop serving both scales; demo artifacts regenerated | `2026-07-08-evolution-at-16x16.md` |

**Every standing gate is green at 16×16 and no 8×8 pin moved** — the
final sweep: 16 labs (grid_genome 209, workshop_editor 307,
cellular_automata 37, runtime 65, game_loop 83, map_elites 35, …),
package 291, workshop 58, CLI 21. Size-parametric, never
size-replacing: the 8×8 corpora, gates, and demo history remain valid
input and valid evidence.

## HONEST REMAINDER — what still runs at 8×8 only, and why

1. **The generation token alphabet** is still {., B, A, E, M}: children
   bred from rich 16×16 parents keep core/eyes/mouth but lose
   shell/limb/antenna cells. This is exactly Phase B's charter — the
   WFC/constraint layer over the full vocabulary, then the REAL
   documented bake-off.
2. **Readability calibration**: the learned model (F3) was trained on
   8×8 corpora; it scores 16×16 grids but its calibration is
   8×8-derived, and it is displayed as uncalibrated at scale. The human
   survey remains the owner-deferred fallback, never a blocker;
   retraining on 16×16 data enters when Phase B/C produce the corpora
   it needs.
3. **Animation**: the projections and `animstate_300` are 8×8 corpora —
   the animation SYSTEM (clips, frames, transitions) does not exist at
   any scale; that is Phase C, not a Phase-A leftover.
4. **The datasets program** (mechaseed_200, mutationbench_5000,
   replay_100k_ticks) is 8×8 data — valid history, regenerated at scale
   only when a consumer needs it (their consumers are Phase D/E work).
5. **The editor's default canvas** still opens at 8×8 (the 16×16 button
   is one click); the rich-vocabulary PAINTING alphabet remains the T9
   trait-editor charter.
6. **The vocabulary exemplar** (ARGUS) is 8×8 — its coverage pin is now
   doubly covered by the 16×16 corpus, so it stays as history.

## VERDICT

**Phase A is green.** The engine's foundation — invariants, corpus,
validator, generation, repair, lifecycle, SLIP, archive, evolution, and
the session surfaces — is proven at the documented primary scale with
the 8×8 evidence base intact. Cycle 09 is complete; cycle 10 opens
Phase B from the gap analysis: `labs/wfc_grid/` and the real documented
bake-off.

## Verification

```powershell
PS> # the closing sweep (2026-07-08)
architecture 14 OK · asset_pipeline 22 OK · cellular_automata 37 OK ·
ctm_ticks 4 OK · cubff_transducer 17 OK · datasets 22 OK ·
game_loop 83 OK · grid_genome 209 OK · lifecycle_sim 24 OK ·
map_elites_archive 35 OK · package_promotion 6 OK ·
readability_benchmark 42 OK · repair_boundary 4 OK ·
runtime_integration 65 OK · slip_validator 24 OK ·
workshop_editor 307 OK · package 291 OK · workshop 58 OK · CLI 21 OK
PS> python -B labs/package_promotion/package_promotion_gate.py
"promotion_ready_count": 9   # steady
```

## Sources

- `docs/gap-analysis.md` (Phase A), `audits/TODO.md` (cycle 09)
- The five A-task reports (2026-07-08): `16x16-invariant-scaling`, `16x16-seed-corpus`, `16x16-validator-generation`, `stress-probe-scaling`, `repair-at-16x16`, `slip-size-relative-bounds`, `evolution-at-16x16`
- `research/decision_records/0029-16x16-default-grid-scale.md`, `0030-slip-size-relative-mass-bounds.md`
- `research/grid_genome/grid_invariants.md` (the ratified tables)
- `data/seed_grids_16x16/`, `data/invalid_grids_16x16/`, `data/grid_genome/`, `data/archives/stress_probe_scaling_stage0.json`, `data/game_loop/`
