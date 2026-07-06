# mecha_engine SLIP v0.2 + Render Packet v2 Port (DR 0013)

Date: 2026-07-05. Status: `package_v2_ports_landed_contract_evidence`.

## What changed

Owner-authorized promoted-module changes ("authorized --go"), executed
by sub-agent under a spec-first brief, orchestrator-verified:

- All four private `_slip` mirrors: lab-verbatim dual-version validation
  (0.1.0 frozen / 0.2.0 + four ladder fields) and forbidden-traits
  alignment enforcement, error strings byte-identical.
- `lifecycle.initial_state` stashes `risk_tolerance_mutation` +
  `learning_switches` for v0.2 profiles (v0.1 byte-identical);
  `lifecycle/_policy.py` synced too — a sub-agent-caught necessity its
  own v0.2 full-episode parity pin proves (episodes CONSUME the stash).
- `learning/_switchboard.py`: registry + gating + tolerance, verbatim.
- `runtime.evolve` honors `lineage_preferences.parent_selection`
  (fitness-weighted `(-fitness, niche)` ordering; defaults byte-identical).
- `genome/animation.py` (additive publics): `ANIMATION_STATES`,
  `project_animation_state`, `render_packet_v2`;
  `render_packet_from_grid` untouched. v0.2 profiles now drive package
  simulations natively — no projection needed.

## Verification (orchestrator-independent)

```txt
packages tests   Ran 266 (was 235)  OK   git diff: zero deletions in any test/driver — no existing pin touched
grid_genome 137 / lifecycle_sim 19 / runtime_integration 42  OK
boundary scan: 0 matches
scaffold gate 9/9 (import_suite 266); promotion gate 7/8 promotion_ready
```

## Honest scope notes (from the port, kept)

- Evolve full-run parity is pinned for lineage-only v0.2 profiles
  (lifecycle-transparent, hence byte-identical to the lab's projected
  run); tolerance/switch-carrying profiles run natively in the package
  while the lab loop still projects — the documented follow-up is the
  lab-side `v01_projection` retirement experiment.
- The runtime v2 probe uses a grid-dependent scorer because the suite's
  constant scorer ties all fitness and masks the ordering rung.

## Sources

- `research/decision_records/0013-port-slip-v2-and-packet-v2.md`
- `packages/mecha_engine/src/mecha_engine/` (four `_slip.py`, `lifecycle/simulate.py`, `lifecycle/_policy.py`, `learning/_switchboard.py`, `runtime/evolve.py`, `genome/animation.py`)
- `labs/grid_genome/test_package_slip_parity.py`, `test_package_switchboard_v2_parity.py`, `test_package_animation_parity.py`
- `labs/lifecycle_sim/test_package_lifecycle_v2_parity.py`, `labs/runtime_integration/test_package_evolve_parenting_parity.py`
- `data/architecture/mecha_engine_scaffold_verification_gate_stage0.json`
