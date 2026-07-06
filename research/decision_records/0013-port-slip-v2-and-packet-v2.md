# Decision Record 0013: Port SLIP v0.2 and Render Packet v2 into mecha_engine

Date: 2026-07-05

## Status

**Accepted** (owner: "authorized --go", 2026-07-05). Authorizes the two
promoted-module changes the ladder and T16 left DR-gated: the package's
SLIP surfaces learn the v0.2 ladder, and `mecha_engine.genome` gains the
animation/packet-v2 publics. Lab semantics are the source of truth
(ports verbatim; parity pins on frozen v0.1 flows must stay green
untouched).

## Scope

1. **SLIP v0.2 across the package `_slip` mirrors** (generation,
   lifecycle, repair, runtime — private copies): dual-version
   `validate_slip` (0.1.0 baseline exact; 0.2.0 adds the four optional
   ladder fields with the lab's exact validation semantics and error
   strings) and `is_grid_aligned` forbidden-traits enforcement.
2. **Lifecycle consumers**: `initial_state` stashes
   `risk_tolerance_mutation` and `learning_switches` for v0.2 profiles
   exactly as the lab lifecycle does (v0.1 states byte-identical).
3. **Learning consumers**: the `_switchboard` mirror syncs to the lab's
   current semantics — thread registry, learning-switch gating, and the
   tolerance flip-point in the mutation-risk thread (absent keys =
   frozen behavior; `decide` parity over v0.1 trajectories unchanged).
4. **Runtime consumer**: `evolve` honors
   `lineage_preferences.parent_selection` (fitness_weighted elite
   ordering, lab semantics) when the profile carries it; default flows
   byte-identical.
5. **Genome additive publics** (no change to existing surfaces):
   `ANIMATION_STATES`, `project_animation_state`, and
   `render_packet_v2(grid, lifecycle_state=None, *, animation=None)` —
   verbatim ports of the T4/T16 lab semantics (selection thresholds
   mirrored with citation). `render_packet_from_grid` stays exactly v1.

## Gates

- Every touched module: contract tests extended for the v0.2/v2 paths;
  lab-side parity tests pin package == lab on both v0.1 (frozen) and
  v0.2 (new) inputs, error strings included.
- Boundary scan stays zero; all existing parity pins pass UNMODIFIED —
  any pin edit is a red flag, not a fix.
- After the port, `v01_projection` remains valid for older package
  consumers but the evolution lab may pass full v0.2 profiles through;
  the lab keeps the projection until the port lands and its own tests
  say otherwise (follow-up experiment, not this DR).

## Sources

- `research/decision_records/0012-slip-schema-extension-ladder.md` (rule 4)
- `audits/TODO.md` (T3, T16)
- `labs/grid_genome/slip.py`, `labs/grid_genome/micro_switchboard.py`, `labs/grid_genome/animation_states.py`
- `labs/lifecycle_sim/lifecycle_sim.py`, `labs/runtime_integration/mecha_engine_runtime_loop.py`
- `research/experiment_reports/2026-07-05-slip-ladder-*.md`, `2026-07-05-render-packet-v2.md`
