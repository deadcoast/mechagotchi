# mecha_engine Lifecycle Module Promotion

Date: 2026-07-04

Status: `package_lifecycle_module_promoted_contract_evidence`

## Purpose

Execute the third module promotion into `packages/mecha_engine`, per the
traceability matrix order (genome → generation → **lifecycle** → archive →
provenance), against
`research/package_specs/mecha_engine_module_interfaces.md` and
`research/package_specs/mecha_engine_lifecycle_contract_gate.md`.

## What changed

`packages/mecha_engine/src/mecha_engine/lifecycle/` implements the full
contracted surface, self-contained (stdlib only, no `labs` imports, no
artifact writes, typed):

- `simulate.py` — `initial_state` / `advance_tick` / `run_episode` /
  `reward_for_transition`: verbatim semantic port of the Stage 0 research
  lifecycle simulator (identical need-decay drift, action effects, recovery
  counting, explicit death causes, per-tick history entries, and the pinned
  survival_ticks death-tick arithmetic). Grids are rejected through
  `mecha_engine.genome.validate_grid` before any state exists.
- `_policy.py` — documented frozen policy factoring: the interface spec and
  contract gate keep learning lab-only (`learning` is a deferred module), so
  lifecycle carries only the *frozen* micro-switchboard decision function
  (identical thread math and tie-break ordering) plus the Stage 0
  pre-policy safety overrides needed to reproduce the pinned comparator.
  No module-level learner memory, no persistence across episodes, no
  reward-shaping update path (that remains the grid_genome
  switchboard-feedback research lab).
- `_slip.py` — documented minimal internal SLIP port, mirroring the
  factoring already promoted for `mecha_engine.generation` (the scaffold
  defers `slip`); validates supplied profiles and grid alignment before
  profile-weighted state creation.

Package tests (`test_lifecycle_contract.py`, 31 tests, same subprocess
mechanics as genome/generation) prove the contract gate: the Stage 0
switchboard/idle/random comparator table exactly, bounded state at every
forced continuous-state corner across all five actions, the four explicit
death causes, full-horizon need-balance scoring with 0.0 post-death fill,
determinism per RNG seed, action-stream support with ambiguity rejection,
invalid grid/profile rejection before simulation, bounded pure rewards
with the four recovery signals, and no online learner memory across
episodes. Lab-side parity
(`labs/lifecycle_sim/test_package_lifecycle_parity.py`, 7 tests) pins
package output against `run_lifecycle_simulation`: byte-identical initial
states, single transitions for every action, and full episode reports (no
excluded keys) across policies, horizons (48/72/96/200), seeds, grids, and
the no-profile path.

Documented spec resolutions: `rng_seed=None` defaults deterministically to
the pinned Stage 0 seed `20260512` (the lab default, asserted in parity);
`policy=None` with `actions=None` uses the Stage 0 default policy
`switchboard`; supplying both a policy and an action stream is rejected as
ambiguous; an explicit action stream must cover the requested tick horizon
(death may consume fewer actions) and reports `policy: null`; the
episode-scoped `action_rewards` ring buffers (bounded to the last 8
samples, living only inside returned state) are Stage 0 simulator state
consulted read-only by the frozen switchboard, not learner memory.

## Result

- Stage 0 comparator reproduced exactly: switchboard 72/alive/0.789129/14,
  idle 11/dead/0.121004/starvation, random 21/dead/0.236001/starvation.
- Full-dict episode parity with the lab simulator (zero divergent keys).
- Invalid grids, invalid SLIP profiles, misaligned grids, unsupported
  actions/policies, and ambiguous requests all rejected before simulation.
- 160-transition corner sweep keeps every continuous variable in [0, 1];
  every death carries an explicit contracted cause.
- Identical requests reproduce identically after interleaved episodes: no
  online learner memory in the package.
- Boundary scan over `packages/mecha_engine`: zero matches.

```powershell
python -B -m unittest discover -s packages/mecha_engine/tests -p "test_*.py"
# Ran 83 tests - OK  (was 52; +31 lifecycle contract)
```

Scaffold verification gate: `promoted_modules` now
`["genome", "generation", "lifecycle"]`, 9/9 checks pass, artifact
regenerated. Full sweep: 502 lab tests (was 495; +7 lifecycle parity) + 83
package tests, all green. The package-promotion gate rerun
(`data/package_promotion`) is deferred to the orchestrated promotion-gate
step and not rerun here.

## Decision

`mecha_engine.lifecycle` is promoted with contract evidence. Online reward
shaping, contextual-bandit learner memory, and feedback learners remain
lab-only per the contract gate. Next module in the traceability order:
`archive`.

## Verification

```powershell
python -B -m unittest discover -s packages/mecha_engine/tests -p "test_*.py"
python -B labs/lifecycle_sim/test_package_lifecycle_parity.py
python -B labs/lifecycle_sim/test_lifecycle_sim.py
python -B labs/architecture/mecha_engine_scaffold_verification_gate.py
python -m json.tool data/architecture/mecha_engine_scaffold_verification_gate_stage0.json
```

## Sources

- `research/package_specs/mecha_engine_module_interfaces.md`
- `research/package_specs/mecha_engine_lifecycle_contract_gate.md`
- `research/package_specs/mecha_engine_contract_traceability_matrix.md`
- `research/package_specs/mecha_engine_property_negative_test_strategy.md`
- `data/architecture/mecha_engine_lifecycle_contract_gate_stage0.json`
- `data/lifecycle/lifecycle_stage0.json`
- `labs/lifecycle_sim/lifecycle_sim.py`
- `labs/grid_genome/micro_switchboard.py`
- `labs/grid_genome/slip.py`
- `packages/mecha_engine/src/mecha_engine/lifecycle/`
- `packages/mecha_engine/tests/test_lifecycle_contract.py`
- `labs/lifecycle_sim/test_package_lifecycle_parity.py`
- `research/experiment_reports/2026-07-04-mecha-engine-generation-promotion.md`
