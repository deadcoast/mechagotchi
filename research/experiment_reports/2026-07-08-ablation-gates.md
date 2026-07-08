# Experiment Report: The Ablation Gates — Kept and Dropped Without Sentiment (Cycle 12 · ENGINE · D6)

Date: 2026-07-08

## WHY

The dossier's micro-learner ablation prescribes the discipline: five
user models, remove-one conditions, and the decision gate — "keep a
learner only if its removal causes at least a 5% decline in one target
metric without improving another more important one"; the bandit-track
welfare gate is "≥15% over rules". D5 delivered the harness and an
honest zero that forced the environment redesign D6 runs in.

## WHAT

`labs/micro_threads/ablation_gates.py` (RED-first; the lab is now 85
tests): the KEEPER-DEPENDENT BEG-MEDIATED mode — the companion cannot
feed itself; its autonomous "feed" decision is a beg display, and each
keeper personality answers the beg its own way (attentive 0.9,
neglectful 0.08, punitive answers with the WRONG action). Welfare =
the engine's own balance summed over REQUESTED ticks (death costs —
the lifetime metric folded in). Fourteen conditions at full scale
(100 lifecycles × 5 keepers × 200 ticks each): `rules_only` (every
thread off — the T19 precedent), `frozen` (the promoted switchboard),
`full_fleet` (all 11), and `minus_<thread>` × 11, paired seeds.
Verdict rule: keep on ≥5% welfare removal cost OR ≥5% on the thread's
own documented skill metric (read from the D2/D3 artifacts).

## FINDINGS (full scale, both gate readings recorded)

- **The documented gate is MET: full fleet beats `rules_only` by
  292.6%** (the dossier's "≥15% over rules"; T19's full-vs-rules-only
  headline of +335% is the precedent).
- **The stricter reading is NOT met and recorded, not hidden:
  fleet-vs-frozen is −0.054%.** Measured across three environments
  (sheltered, state-keyed dependent, beg-mediated dependent) and an
  anticipation-gain sweep (best +0.6% at gain 6; gain 10 harmful):
  the frozen reactive rules already sit near the autonomous-behavior
  welfare optimum — the remaining welfare belongs to the KEEPER. The
  fleet's proven value is prediction skill, personalization, and
  interpretability, streamed for the game's consumers — not
  decision-seam welfare.
- **Verdicts, without sentiment — 5 kept, 6 dropped:**

| Thread | Verdict | Welfare removal cost | Own skill metric |
| --- | --- | --- | --- |
| hunger_forecast | **keep** | +0.38% | 37.9% MAE improvement vs persistence |
| energy_forecast | **keep** | 0.0% | 53.7% |
| interaction_timing | **keep** | −0.22% | 14.8% gap-MAE vs last-gap |
| animation_bandit | **keep** | 0.0% | 65.6% regret reduction vs rotation |
| hidden_mood_hmm | **keep** | −0.05% | 50.1% Brier reduction vs persistence |
| boredom_novelty | **DROP** | −0.22% | 4.59% — under the 5% bar |
| attention_forecast | **DROP** | −0.22% | 2.31% — under the 5% bar |
| mutation_stability | **DROP** | 0.0% | none (evidence conduit) |
| readability | **DROP** | 0.0% | none (evidence conduit) |
| slip_compat | **DROP** | 0.0% | none (evidence conduit) |
| lineage_survival | **DROP** | 0.0% | none (evidence conduit) |

- Per the T19 precedent, dropped threads stay in the registry as
  parity-pinned code with their verdicts recorded; default profiles
  must not opt them in. The evidence conduits' D4 wiring remains the
  input plumbing for selection/packet consumers — their drop is from
  the DECISION seam. The post-drop fleet of five has no dead-weight
  member (the Stage-5 exit shape).

## Verification

```powershell
PS> python -B -m unittest discover -s labs/micro_threads -p "test_ablation_gates.py"   # RED
ImportError (module ablation_gates does not exist)
PS> python -B -m unittest discover -s labs/micro_threads -p "test_*.py"   # GREEN
Ran 85 tests in 8.359s
OK
PS> python -B labs/micro_threads/ablation_gates.py
full_vs_rules_only_welfare_pct: 292.649 (meets 15%: true)
fleet_vs_frozen_welfare_pct: -0.054
5 threads kept, 6 dropped by the documented rule.
```

## Sources

- `labs/micro_threads/ablation_gates.py` (+ `test_ablation_gates.py`)
- `data/micro_threads/ablation_gates_stage0.json`
- `data/micro_threads/need_predictors_stage0.json`, `animation_bandit_hmm_mood_stage0.json` (the skill metrics)
- `data/micro_learners/switchboard_ablation_stage0.json` (the T19 precedent)
- `labs/micro_threads/synthetic_keepers.py` (D5's harness + honest zero)
- `docs/project-research/deep-research/01/deep-research.md` (the gates)
- `audits/TODO.md` (cycle 12 D6), `docs/gap-analysis.md` (Phase D)
