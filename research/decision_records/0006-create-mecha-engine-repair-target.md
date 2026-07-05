# Decision Record 0006: Create the Mecha Engine Repair Package Target

Date: 2026-07-05

## Status

Accepted. Authorizes creating `packages/mecha_engine/src/mecha_engine/repair`
and promoting the wound-site learned repair surface under the existing
promotion-gate rules.

## Context

Decision record 0004 deferred the `repair` module "until current blockers are
resolved". That blocker — `lab_only_target_template_assisted` — was static
with null evidence until 2026-07-04, then derived from the trained-repair
artifact, and now measures cleared:

- The wound-site learned repair arm meets the assisted stability bar on
  held-out grids over five compounding damage cycles: final overlap
  0.938462, structural agreement 0.938462, validity 1.0 (guarded);
  0.930769 / 0.930769 / 0.9 with the validity guard off. It uses no target
  template and no destroyed-token memory — only the damage event's
  destroyed positions, an engine-native signal.
- The blind arm honestly remains below the bar (0.862546 / 0.631871 / 1.0;
  `meets_assisted_stability_bar = false`) and stays in the benchmark as the
  record of observability-free repair.
- Retrieval-context conditioning is a recorded negative result, and the
  exemplar-retrieval ceiling (0.785) bounds the retrieved-template family
  below the bar on this corpus.
- The promotion gate reports the `ca_nca_repair` candidate as
  `ready_for_package_design` with `target_package_absent` as its only
  promotion blocker.
- The interface is specified:
  `research/package_specs/mecha_engine_repair_interface_spec.md`, with a
  repair row in the contract traceability matrix.

The user explicitly authorized this scope step on 2026-07-05.

## Decision

Create the sixth package module target:

```txt
packages/mecha_engine/src/mecha_engine/repair/
```

and promote the wound-site repair surface into it under the same rules as
the five initial modules:

- Public surface (from the interface spec): `train_repair_model(...)` and
  `repair_wound_sites(damaged_grid, model, *, wound_sites=None,
  validity_guard=True)`. The blind neighborhood repair may be exposed as an
  explicitly labelled benchmark comparator; the template-assisted attractor
  is NOT ported (the genome-template path stays out of this module so the
  no-template property is structural).
- The observability contract is part of the module contract: damage events
  report destroyed positions (`removed_cells`), never destroyed tokens,
  never a template; `target_template_used` is `false` on every result.
- Port keeps lab semantics verbatim (weights, fill order, guard
  substitutions, metadata, error strings), pinned by a lab-side parity test
  over the corpus and by contract tests run through the package `src`
  surface in a subprocess — no `sys.path` text anywhere in the package
  tree; package code imports `mecha_engine.genome` for validation, never
  `labs`.
- Stdlib-only, deterministic, typed, `@dataclass`-style result conventions
  consistent with the existing modules.
- `tests/test_package_imports.py` moves `repair` from the deferred list to
  the promoted import surface; the promotion gate is re-run after the
  target exists and must report the candidate `promotion_ready` before the
  port lands, and `promoted` semantics (contract tests green) after.

## Consequences

- `mecha_engine` gains its first module promoted after the initial five —
  the promotion pipeline is exercised end-to-end a second time, now
  including the blocker-derivation path.
- The engine's damage surfaces inherit a hard requirement: any future
  lifecycle/gameplay damage event must report destroyed positions, or
  repair degrades to the blind arm's measured (below-bar) quality.
- `learning`, `render`, `storage`, and `slip` remain deferred; this record
  authorizes only `repair`.
- The package dependency policy remains blocked; the repair module adds no
  dependencies.

## Evidence

- `research/decision_records/0004-mecha-engine-package-scaffold.md`
- `research/package_specs/mecha_engine_repair_interface_spec.md`
- `research/package_specs/mecha_engine_contract_traceability_matrix.md`
- `research/experiment_reports/2026-07-04-ca-nca-wound-site-repair.md`
- `research/experiment_reports/2026-07-04-ca-nca-wound-site-validity-guard.md`
- `research/experiment_reports/2026-07-04-ca-nca-repair-context-ablation.md`
- `data/cellular_automata/ca_nca_trained_repair_stage0.json`
- `data/cellular_automata/ca_nca_repair_context_ablation_stage0.json`
- `data/package_promotion/mecha_engine_package_promotion_gate_stage0.json`
