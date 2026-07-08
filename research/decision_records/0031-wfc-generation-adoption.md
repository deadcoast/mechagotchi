# Decision Record 0031: WFC Adopted as the Rich-Alphabet Generation Architecture

Date: 2026-07-08

## Status

**Accepted** (cycle 10 · ENGINE track · Phase B, task B3). The adoption
the gap analysis' Phase B exists for, decided by the B2 bake-off under
a rule pre-registered before the run.

## Context

The documents specified Markov → WFC/constraints → mutation → validator
as the winning generation architecture, but no WFC lab ever existed and
the historical bake-off ran without the documented field. Phase A left
the matching remainder: the generation alphabet was {., B, A, E, M}, so
children of rich parents lost their shells, limbs, and antennae. B1
built the constraint layer over the full DR 0015 alphabet; B2 ran the
real bake-off — all five arms, dossier metrics, thresholds ≥0.85
validity and ≤250 ms per candidate at 16×16.

## The measured verdict (B2, pre-registered rule)

- **WFC wins**: validity 1.0, organ-presence F1 0.96, all 100
  silhouettes unique, descriptor novelty 0.25, zero training copies,
  6.3 ms per candidate (≈40× under the time bar), full rich alphabet.
- **The documented hybrid is REFUTED** at this scale (first-class
  finding): its additions over WFC are the mutation-temperature jitter
  — invisible to the baseline descriptor axes — and a validator gate
  that never fires because the collapse already emits valid creatures;
  the pipeline's Markov stage is already inside the collapse's proposal
  distribution. Nothing is lost: the promoted `evolve` applies its own
  jitter, and the extended archive's mutation_stability axis is fed
  there.
- `constrained` clears validity with the best readability and novelty
  but cannot emit the rich alphabet — barred by the requirement this
  phase exists to satisfy; it remains the promoted 4-token parent-based
  surface, untouched.
- `markov` measured 2% valid at 16×16 (global-connectivity blindness);
  `random` 46% valid with 53% training copies — the honest floors.

## Decisions

1. **`mecha_engine.generation` gains the WFC surface** as an ADDITIVE
   seam: `train_wfc_model`, `generate_wfc_grid`, `build_wfc_corpus` —
   a verbatim semantic port of the lab (identical model dictionaries,
   RNG streams, error strings, and source labels), pinned by the
   lab-side parity test over trained models and full corpora. Every
   existing generation surface is byte-identical.
2. **WFC is the production generator for rich-alphabet 16×16
   generation**; the constrained stabilizer remains the 4-token
   parent-based path (the workshop's offspring preview and `evolve`'s
   candidate loop keep it — moving evolve's inner loop onto WFC is a
   separate future decision with its own evidence, not smuggled in
   here).
3. **The hybrid refutation is recorded, not retried**: re-opening it
   requires an axis on which the jitter/gate stages can show value
   (e.g. an extended-descriptor bake-off), named here as the re-opener.
4. Stdlib holds (6.3 ms/candidate measured); no dependency enters
   (DR 0028 policy, Phase A's measurement precedent).

## Sources

- `research/experiment_reports/2026-07-08-generation-bakeoff-16x16.md` (the verdict)
- `research/experiment_reports/2026-07-08-wfc-grid-lab.md` (B1)
- `labs/wfc_grid/` (lab + bake-off + parity pin), `data/wfc_grid/`
- `packages/mecha_engine/src/mecha_engine/generation/wfc.py`
- `packages/mecha_engine/tests/test_generation_contract.py` (the widened public surface)
- `docs/gap-analysis.md` (Phase B), `audits/TODO.md` (cycle 10 B3)
- `research/decision_records/0015`, `0028`, `0029`
