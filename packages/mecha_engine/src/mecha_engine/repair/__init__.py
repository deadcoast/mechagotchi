"""Wound-site learned repair contract surface for mecha_engine.

Promoted sixth — the first module promoted after the initial five — per
decision record 0006
(research/decision_records/0006-create-mecha-engine-repair-target.md).
Public surface per
research/package_specs/mecha_engine_repair_interface_spec.md:

- ``train_repair_model(training_grids, ...) -> dict`` — deterministic
  full-batch softmax training over seeded stochastic-damage examples;
  identical inputs give identical weights.
- ``repair_wound_sites(damaged_grid, model, *, wound_sites=None,
  validity_guard=True) -> dict`` — wound sites default to the damage
  event's ``removed_cells``; most-confident-first fill; fully
  deterministic, including validity-guard substitutions.
- ``repair_blind(damaged_grid, model, *, steps=8) -> dict`` — the
  explicitly labelled benchmark comparator for observability-free repair;
  its measured quality stays below the assisted stability bar.

Observability contract (load-bearing, from the interface spec): any damage
event reports which positions it destroyed (``metadata.removed_cells``) —
never the destroyed tokens, and the repair surface never receives a target
template or the pre-damage grid. Repair fills exactly the reported sites
with model-predicted tokens, so the repaired live-position set equals the
pre-damage live-position set (one-sided overlap equals two-sided
structural agreement identically) and ``target_template_used`` is
``False`` on every model and every repair result. The template-assisted
local attractor is NOT ported, so the no-template property of this module
is structural (decision record 0006). Grid validity inside the wound-fill
guard is checked through ``mecha_engine.genome.validate_grid`` only. The
implementation is self-contained package code (stdlib only, no research
lab imports) and performs no Stage 0 artifact writes on import.
"""

from .blind import repair_blind
from .train import train_repair_model
from .wound import repair_wound_sites

__all__ = [
    "repair_blind",
    "repair_wound_sites",
    "train_repair_model",
]
