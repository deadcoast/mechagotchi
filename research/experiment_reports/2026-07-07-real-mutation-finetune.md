# Experiment Report: Real-Mutation Fine-Tune (F3) — All Gates Green, Adopted

Date: 2026-07-07

## WHY

E3 measured the shipped R3 model at 0.983 on physics-DEGRADED real
mutation pairs but 0.849 on physics-IMPROVED ones — the signature of
training exclusively on synthetic degradations — and named the bench's
physics-labeled pairs "a ready fine-tuning corpus." F3 runs the
falsifiable experiment: augment, gate, adopt only on a full win.

## WHAT

`labs/readability_benchmark/real_mutation_finetune.py` (artifact
`data/readability_benchmark/real_mutation_finetune_stage0.json`):

- **The real corpus** — E3's labeling verbatim over all 5,000 bench
  cases (signatures re-verified; a mismatch raises), monotone physics
  labels only, held out BY PARENT (mg_seed_041–050's cases) so the
  evaluation is cross-parent generalization.
- **The models** — original: R3's exact shipped recipe. Augmented: the
  SAME synthetic training pairs + the real training pairs, same
  trainer, same seed, same corpus-mean anchor (comparable by
  construction).
- **The gates** — (a) real heldout must improve; (b) synthetic heldout
  AND per-family accuracy must not regress; (c) a live physics A/B at
  the same seed (evolve steered by each model, elites judged by the
  NEUTRAL four-metric physics composite) must not be worse.

## RESULT — adopt

| Gate | Original | Augmented | Verdict |
| --- | --- | --- | --- |
| Real heldout (cross-parent) | 0.98018 | **1.0** | improved |
| Synthetic heldout | held | held | no regression |
| Synthetic per-family (×4) | held | held | no regression |
| Live physics composite | 0.832844 | 0.832844 | not worse (identical elites at this seed) |

**`adopt_augmented_model`** — and the follow-through shipped: the
adopted weights are FROZEN as a committed, auditable artifact
(`data/readability_benchmark/adopted_readability_model.json`, with
provenance and its regenerator named — the R3 doctrine that learned
weights are inspectable data). The session's `train_legibility_model`
now LOADS the artifact (deterministic, faster than retraining; the
original recipe remains the honest fallback if the artifact is absent),
so the Keeper's legibility currency runs on the real-mutation-hardened
model everywhere. Session artifacts regenerated; every suite green.

## Verification

```powershell
PS> python -B labs/readability_benchmark/real_mutation_finetune.py
{ "decision": "adopt_augmented_model",
  "gates": {all four: true},
  "real_heldout": {"original": 0.98018, "augmented": 1.0} }

PS> sweep: readability_benchmark (42) OK · game_loop (69) OK ·
    datasets (22) OK · runtime_integration (65) OK · package (290) OK ·
    workshop OK
```

## Decision

Adopt — F3 developed to its description with a full-win verdict decided
by measurement. The manual rating system remains the fallback and
calibration check throughout (DR 0019, unchanged).

## Sources

- `research/experiment_reports/2026-07-07-dataset-consumers.md` (the seed)
- `research/decision_records/0019-learned-readability.md`
- `labs/readability_benchmark/real_mutation_finetune.py`
- `data/readability_benchmark/real_mutation_finetune_stage0.json`
- `data/readability_benchmark/adopted_readability_model.json`
- `labs/game_loop/session_runner.py` (the switched trainer)
