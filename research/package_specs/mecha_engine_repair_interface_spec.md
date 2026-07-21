# Mecha Engine Repair Module Interface Spec

Date: 2026-07-04

## Status

Research interface specification for `mecha_engine.repair`. Originally
written 2026-07-04 as a design-only spec while the package target was
decision-record-gated; decision record 0006 (2026-07-05) authorized the
target, and the module was promoted the same day with package contract
tests (`packages/mecha_engine/tests/test_repair_contract.py`) and a
lab-side parity pin
(`labs/cellular_automata/test_package_repair_parity.py`). This document is
now the module's contract reference; the hard gates below are enforced by
those tests.

## Why this module can be specified now

The `lab_only_target_template_assisted` blocker cleared on 2026-07-04: the
wound-site learned repair arm meets the assisted stability bar
(overlap 0.938462, structural agreement 0.938462, validity 1.0 on held-out
grids over five compounding damage cycles) with no target template and no
destroyed-token memory. The blind arm honestly remains below the bar
(0.862546 / 0.631871 / 1.0) and retrieval-context conditioning is a recorded
negative result. The interface below is therefore built around the one
observability assumption the evidence supports: **damage events report which
cells they destroyed.**

## The observability contract (load-bearing)

Any engine surface that damages a creature MUST report the destroyed
positions. Repair quality depends on it: without site information the best
measured template-free repair is 0.8625 overlap / 0.6319 agreement; with it,
0.9385 / 0.9385 / 1.0.

1. A damage event carries `removed_cells: list[[x, y]]` — positions that
   were live before the event and empty after it. Exactness matters: a
   position that was healed by the event itself (e.g., an anchor reseed
   promoting a surviving cell) is not a removed cell.
2. The event NEVER carries the destroyed tokens, and the repair surface
   NEVER receives a target template or the pre-damage grid. Restoring
   remembered tokens is undo, not repair; the genome-template path already
   exists as the assisted attractor and must stay a separate, explicitly
   labelled surface.
3. Repair fills exactly the reported sites — never more (no overgrowth by
   construction), never fewer (every site refilled with some live token).
   Consequently the repaired live-position set equals the pre-damage
   live-position set, and one-sided overlap equals two-sided structural
   agreement identically. A future package test should assert this
   invariant directly.

## Data contracts

### DamageEvent (today: damaged grid `metadata`)

Required fields:

- `removed_cells: list[[int, int]]`
- `removed_cell_count: int` (== `len(removed_cells)`)
- `damage_event_index: int`
- `damage_pattern: str`

### RepairModel

Required fields (from `train_neighborhood_repair_model`):

- `model_id`, `source_mode`
- `weights` (per-class rows over the fixed feature layout)
- `training_grid_ids`, `example_count`, `feature_count`, `class_tokens`
- `rng_seed`, `epochs`, `learning_rate`, `live_class_weight`
- `initial_loss`, `final_loss`
- `target_template_used: false` (hard invariant)
- `vocabulary` (DR 0041) — recorded ONLY when non-legacy (`"rich"`:
  the 11-class head over the full ratified live alphabet, identity
  perception). Absent = legacy: the historical 5-class head with the
  DR 0039 coarsening, byte-identical. Consumers derive the class
  alphabet from the model (`vocabulary` + `class_tokens` must agree,
  refused loudly otherwise); `train_repair_model` gains the
  keyword-only `vocabulary="legacy"` parameter.

### RepairResult (today: repaired grid + `metadata`)

Required metadata fields:

- `learned_model_id`
- `target_template_used: false`
- `wound_site_count: int`
- `validity_guard_substitutions: int`

## Required public surface

- `train_repair_model(training_grids, ...) -> RepairModel` — deterministic
  full-batch training; identical inputs give identical weights.
- `repair_wound_sites(damaged_grid, model, *, wound_sites=None,
  validity_guard=True, slip_profile=None) -> grid` — wound sites default
  to the damage event's `removed_cells`; most-confident-first fill; fully
  deterministic. `slip_profile` (added 2026-07-05 after the runtime
  integration finding) is the engine-native constraint set active at
  runtime; with it, the guard also repairs SLIP alignment. Default `None`
  keeps prior behavior bit-identical (the trained-repair benchmark
  artifact is unchanged).
- The blind arm (`repair_with_neighborhood_model`) and the assisted
  template attractor (`repair_with_local_attractor`) remain benchmark
  comparators; if exposed, the assisted surface must be labelled
  template-assisted.

## Validity-guard semantics (part of the contract)

- Signal: the target-free grid validator — plus, when the active
  `slip_profile` is supplied, SLIP alignment errors (combined error
  count). The profile constrains every creature of its kind (palette
  legality, required organ roles, mass bounds) and carries nothing about
  the individual's silhouette or destroyed tokens, so the no-template
  property is preserved. Consequence to state honestly: with a profile,
  the guard repairs the *constraint* (e.g. "an expression cell exists"),
  not the individual's exact token placement — the restored organ cell
  may sit at a different wound site than the destroyed one.
- Without a profile: no template, no tokens, validator only (unchanged).
- Moves: substitute an alternative live token at a wound site. Sites are
  never emptied; non-site cells are never touched.
- Order: sites ascending by fill confidence (least confident first);
  alternative tokens descending by model probability, class-index
  tie-break.
- Acceptance: strict reduction of the validation error count.
- Termination: passes bounded by site count; deterministic.
- Reporting: substitution count in the repair result. The guard guarantees
  invariant repair when reachable by single-token substitutions, not token
  correctness.

## Hard gates for a future package port

- Reproduce the lab benchmark verbatim (lab-parity pin over the same
  corpus, seeds, and cycles): site-aware arm >= 0.9 on final overlap,
  structural agreement, and validity; recorded values 0.938462 / 0.938462 /
  1.0 (guarded) and 0.930769 / 0.930769 / 0.9 (guard off).
- Assert the live-position invariant (overlap == agreement for the
  site-aware arm) and `target_template_used == false` on every result.
- Keep the blind arm's unmet bar in the benchmark permanently
  (`meets_assisted_stability_bar` currently `false`) — it is the honest
  record of observability-free repair.
- Deterministic: identical inputs give identical repaired cells, including
  guard substitutions.
- SLIP-aware guard (2026-07-05): with the active profile, a
  validator-valid but profile-unaligned refill must be repaired into a
  creature `mecha_engine.lifecycle.initial_state` accepts (the public
  cross-module oracle); without a profile, behavior is bit-identical to
  the pre-extension contract. Both pinned by the contract driver's
  `slip_aware_guard` probe and the lab-side slip-aware parity test.
- Stdlib-only, like the five promoted modules.

## Non-goals

- No package target creation (decision-record-gated).
- No retrieval/exemplar conditioning (rejected negative result:
  `data/cellular_automata/ca_nca_repair_context_ablation_stage0.json`).
- No trained NCA with hidden state (open research, not the next step).
- No claim about damage whose location is unobserved — that case remains
  covered only by the assisted, explicitly template-labelled path.

## Sources

- `labs/cellular_automata/ca_nca_growth_repair.py`
- `labs/cellular_automata/test_ca_nca_growth_repair.py`
- `data/cellular_automata/ca_nca_trained_repair_stage0.json`
- `data/cellular_automata/ca_nca_repair_context_ablation_stage0.json`
- `research/experiment_reports/2026-07-04-ca-nca-wound-site-repair.md`
- `research/experiment_reports/2026-07-04-ca-nca-wound-site-validity-guard.md`
- `research/experiment_reports/2026-07-04-ca-nca-repair-context-ablation.md`
- `research/algorithm_cards/ca_nca_growth_repair.md`
- `research/package_specs/mecha_engine_module_interfaces.md`
- `research/package_specs/mecha_engine_contract_traceability_matrix.md`
- `labs/package_promotion/package_promotion_gate.py`
