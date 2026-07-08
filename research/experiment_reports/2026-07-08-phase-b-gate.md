# Experiment Report: The Phase-B Gate — the Generation Layer Is No Longer Missing (Cycle 10 · ENGINE · B4)

Date: 2026-07-08

## WHY

The gap analysis' generation row: the documented winning architecture
was missing its constraint layer — no `labs/wfc_grid/` existed, the
historical bake-off ran without the documented field, and Phase A's
gate listed the 4-token generation alphabet as its first honest
remainder. Phase B's charter: build the WFC lab, run the REAL bake-off,
adopt the winner.

## THE GATE

| Task | Result | Evidence |
| --- | --- | --- |
| **B1 · the WFC lab** | Exists, over the FULL DR 0015 alphabet. First-class negative result: pure local collapse measured 2% valid (global-connectivity blindness); with the dossier's own recommended stabilizer usage: validity 1.0, 50 unique silhouettes, all six rich roles, zero copies | `2026-07-08-wfc-grid-lab.md` |
| **B2 · the bake-off** | All five arms, batches of 100, adoption rule pre-registered. **WFC wins** (validity 1.0, F1 0.96, 100/100 unique, 6.3 ms/candidate — 40× under the time bar). **The documented hybrid is REFUTED** — its added stages buy nothing on the measured axes. Constrained barred by the rich-alphabet requirement (best readability/novelty otherwise); markov 2%, random 46% with 53% copies — the honest floors | `2026-07-08-generation-bakeoff-16x16.md` |
| **B3 · adoption** | `mecha_engine.generation` gains the WFC surface as an additive seam, verbatim-ported and parity-pinned; every existing surface byte-identical; DR 0031 records the verdict, the refutation's named re-opener, and that evolve's inner loop deliberately stays on the constrained path pending its own evidence | DR 0031 |
| **B4 · corpora + sweep** | `data/generated_grids/wfc_16x16/` (50 candidates) regenerated; full sweep green: 17 labs (wfc_grid 20, grid_genome 209, workshop_editor 307, …), package 291, workshop 58, CLI 21 | this report |

Dossier thresholds: validity 1.0 ≥ 0.85–0.95 ✓; 6.3 ms ≤ 250 ms ✓
(measured, machine-flagged). Protocol adaptations recorded: 30/10/10
split, modal-role F1, entropy/novelty operationalizations, human
pairwise preference not collected (owner-deferred survey).

## HONEST REMAINDER

1. **evolve's candidate loop still breeds through the constrained
   4-token path** — deliberate (DR 0031): moving the evolutionary inner
   loop onto WFC changes parent-inheritance semantics and needs its own
   evidence (offspring resemblance vs novelty). Named as the next
   generation-layer decision, likely alongside Phase E's scale work.
2. **The hybrid re-opener**: an extended-descriptor bake-off where the
   mutation/gate stages could show value on the mutation_stability axis.
3. **WFC candidates carry no parent lineage** (they are seed-corpus
   recombinations, generation 0) — lineage-bearing WFC breeding is part
   of remainder 1.
4. Readability of rich candidates is still judged by the 8×8-calibrated
   proxy (Phase A remainder 2, unchanged).

## VERDICT

**Phase B is green.** The documented generation architecture exists,
was judged by its own protocol, and the measured winner ships in the
engine — with the documented hybrid's refutation recorded as evidence,
not embarrassment. Cycle 10 is complete; cycle 11 opens Phase C from
the gap analysis: the animation system (clips, frames, transitions,
`animstate_300`, the packet's clip/frame_index contract, the retro
effects pipeline — the render-bridge contract the game's client will
consume).

## Verification

```powershell
PS> # the closing sweep (2026-07-08)
architecture 14 · asset_pipeline 22 · cellular_automata 37 · ctm_ticks 4 ·
cubff_transducer 17 · datasets 22 · game_loop 83 · grid_genome 209 ·
lifecycle_sim 24 · map_elites_archive 35 · package_promotion 6 ·
readability_benchmark 42 · repair_boundary 4 · runtime_integration 65 ·
slip_validator 24 · wfc_grid 20 · workshop_editor 307 — all OK
package 291 OK · workshop 58 OK · CLI 21 OK
PS> (Get-ChildItem data/generated_grids/wfc_16x16 -Filter *.json).Count
50
```

## Sources

- `docs/gap-analysis.md` (Phase B), `audits/TODO.md` (cycle 10)
- `research/experiment_reports/2026-07-08-wfc-grid-lab.md`, `2026-07-08-generation-bakeoff-16x16.md`
- `research/decision_records/0031-wfc-generation-adoption.md`
- `labs/wfc_grid/`, `packages/mecha_engine/src/mecha_engine/generation/wfc.py`
- `data/wfc_grid/`, `data/generated_grids/wfc_16x16/`
