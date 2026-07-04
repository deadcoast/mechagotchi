# Experiment Report: CA/NCA Repair Context-Conditioning Ablation (Negative Result)

Date: 2026-07-04

## Objective

The trained-neighborhood-repair report named "a learner with per-grid
context (for example conditioning on the surviving cells' global layout)"
as the next step toward the assisted stability bar. This lab executes that
committed direction and records the honest outcome: it does not work, and
the measurements show why. Negative results are first-class evidence; this
one closes the retrieval-conditioning branch so future sessions do not
re-explore it.

## Scope

All configs share the exact primitives of the main repair lab (features,
softmax trainer semantics, damage seeds, benchmark protocol: 40 training /
10 held-out grids, 5 cycles at dropout 0.2, 8 repair steps, 150 epochs),
imported rather than copied so the comparison stays faithful. Ablated
mechanisms:

- **Retrieval-context features**: leave-one-out top-3 exemplar consensus
  over the training corpus (5 token-consensus fractions + 1 best-match
  confidence, features 161–166) so the softmax can condition on which
  corpus variant the surviving cells resemble.
- **Self-play retraining** (DAgger-style): a second training round on
  masked examples from the model's own repair outputs — the only source of
  positive "this live cell should be empty" prune evidence, and the fix for
  the train/repair distribution shift (training sees fresh damage; repair
  iterates on its own fills).
- **Confidence prune pass**: masked re-evaluation of live cells, deleting
  those the model scores majority-empty, guarded by the target-free grid
  validator (reverted wholesale if a hard invariant breaks).
- **Retrieval ceiling probe**: the best structural agreement any training
  exemplar reaches against each held-out target — an upper bound on every
  repair strategy that converges to a retrieved template.

## Verification

RED (test file for a module that does not exist):

```powershell
python -B -m unittest discover -s labs/cellular_automata -p "test_ca_nca_repair_context_ablation.py"
```

```txt
Ran 1 test in 0.000s
FAILED (errors=1)
```

GREEN (same command after implementation):

```txt
Ran 4 tests in 2.642s
OK
```

Lab command (full-size run, ~4 minutes — trains four models at 150 epochs):

```powershell
python -B .\labs\cellular_automata\ca_nca_repair_context_ablation.py
```

```txt
"plain_replication":      overlap 0.862546  agreement 0.631871  validity 1.0
"context":                overlap 0.802656  agreement 0.615123  validity 1.0
"context_self_play":      overlap 0.809249  agreement 0.590334  validity 1.0
"context_self_play_prune": overlap 0.801557  agreement 0.61331   validity 1.0
"plain_self_play_prune":  overlap 0.838278  agreement 0.589837  validity 1.0
"retrieval_ceiling": mean_oracle_agreement 0.785, mean_retrieved_agreement 0.731124
"decision": "reject_context_conditioning"
```

## Findings

1. **Harness fidelity is proven inside the artifact**: the
   `plain_replication` config reproduces the published blind trained arm
   exactly (0.862546 / 0.631871 / 1.0), so every delta below is attributable
   to the ablated mechanism, not protocol drift.
2. **Context features hurt** (0.862546 → 0.802656 final overlap). The
   failure mode is a train/eval reliability gap: leave-one-out retrieval
   over the training corpus is systematically more reliable than retrieval
   for held-out variants, so gradient descent shifts weight onto consensus
   features that then mislead at evaluation time.
3. **Self-play retraining and pruning do not rescue it**: self-play trades
   agreement for a marginal overlap gain; pruning recovers ~0.02 agreement
   at a small overlap cost. No config approaches the plain rule, let alone
   the 0.9 bar (`best_config_meets_assisted_stability_bar = false`).
4. **The exemplar ceiling bounds the whole family**: the best possible
   training exemplar reaches only 0.785 mean structural agreement against
   held-out targets (`exemplar_ceiling_below_bar = true`), so no
   retrieved-template strategy — however good its retrieval — can clear the
   0.9 agreement bar on this corpus. Per-grid context via corpus retrieval
   is a dead end here; per-grid context via damage-event observability is
   not (see the wound-site report).

## Decision

Status: `reject_context_conditioning`; adoption:
`negative_result_recorded`. The retrieval-conditioning branch is closed
with executable evidence. The blind arm's `meets_assisted_stability_bar`
stays `false` and untouched by this lab. Further repair work routes through
the wound-site observability arm
(`2026-07-04-ca-nca-wound-site-repair.md`). The ablation rules out these
conditioning mechanisms for the linear softmax class, not nonlinear
learners with hidden state — that door stays open but is not the next step.

## Sources

- `labs/cellular_automata/ca_nca_repair_context_ablation.py`
- `labs/cellular_automata/test_ca_nca_repair_context_ablation.py`
- `data/cellular_automata/ca_nca_repair_context_ablation_stage0.json`
- `data/cellular_automata/repair_context_ablation_README.md`
- `data/cellular_automata/ca_nca_trained_repair_stage0.json`
- `research/experiment_reports/2026-07-04-ca-nca-trained-neighborhood-repair.md`
- `research/experiment_reports/2026-07-04-ca-nca-wound-site-repair.md`
- `research/algorithm_cards/ca_nca_growth_repair.md`
