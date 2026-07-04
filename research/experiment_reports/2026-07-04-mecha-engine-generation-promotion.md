# mecha_engine Generation Module Promotion

Date: 2026-07-04

Status: `package_generation_module_promoted_contract_evidence`

## Purpose

Execute the second module promotion into `packages/mecha_engine`, per the
traceability matrix order (genome → **generation** → lifecycle → archive →
provenance), against
`research/package_specs/mecha_engine_module_interfaces.md` and
`research/package_specs/mecha_engine_generation_contract_gate.md`.

## What changed

`packages/mecha_engine/src/mecha_engine/generation/` implements the full
contracted surface, self-contained (stdlib only, no `labs` imports, no
artifact writes, typed):

- `model.py` — `GenerationModel` (frozen dataclass) +
  `train_generation_model` (rejects empty/invalid corpora through
  `mecha_engine.genome.validate_grid`; metadata records strategy, proposal
  source, and a corpus sha256; seeds never mutated).
- `generate.py` — `generate_candidate` / `generate_batch`: verbatim semantic
  port of the lab constrained-WFC-style stabilizer, including the
  2026-07-04 mutation-temperature jitter with the identical rng stream and
  SLIP caps, plus a per-candidate `generation_trace`.
- `_slip.py` — documented minimal internal SLIP port (the interface spec
  defines no package SLIP module and the scaffold defers `slip`, so
  generation carries a private helper with identical error strings).
- `explain.py` — `explain_generation` with all gate-required fields.

Package tests (`test_generation_contract.py`, 28 tests, same subprocess
mechanics as genome) prove the contract gate. Lab-side parity
(`labs/grid_genome/test_package_generation_parity.py`) pins package output
against `build_constrained_corpus`: byte-identical on every key except
`metadata` (the package adds its generation trace; `rng_seed` asserted
equal), for 100 unconstrained + 50 SLIP-constrained candidates, plus a
dedicated jitter-parity test and per-pair `grid_signature` equality.

Documented spec resolutions: `rng_seed=None` defaults deterministically to
seed 0; lineage generation extends parent chains (reducing to the lab's
output for seed parents); `generate_candidate` ids are deterministic
`gen_<sha256(parent_id:seed)[:16]>`; the raw-Markov-not-sole-generator gate
is asserted via strategy labeling, public-surface naming, and 100%
validator-gated traces.

## Result

- 100/100 batch candidates valid through `mecha_engine.genome`, 100 unique
  ids and signatures (baseline 42/100).
- 50/50 SLIP-constrained candidates valid and aligned (independent
  structural oracle + trace evidence).
- Invalid parent / empty corpus / invalid corpus / invalid profile /
  unsatisfiable profile all rejected before generation.
- Determinism per seed; reseeded runs differ; zero input mutations.
- Boundary scan over `packages/mecha_engine`: zero matches.

```powershell
python -B -m unittest discover -s packages/mecha_engine/tests -p "test_*.py"
# Ran 52 tests - OK  (was 24; +28 generation contract)
```

Scaffold verification gate: `promoted_modules` now
`["genome", "generation"]`, 9/9 checks pass, artifact regenerated. Full
sweep: 495 lab tests + 52 package tests, all green.

## Decision

`mecha_engine.generation` is promoted with contract evidence. Next module
in the traceability order: `lifecycle`.

## Verification

```powershell
python -B -m unittest discover -s packages/mecha_engine/tests -p "test_*.py"
python -B -m unittest discover -s labs/grid_genome -p "test_package_generation_parity.py"
python -B labs/architecture/mecha_engine_scaffold_verification_gate.py
python -m json.tool data/architecture/mecha_engine_scaffold_verification_gate_stage0.json
```

## Sources

- `research/package_specs/mecha_engine_module_interfaces.md`
- `research/package_specs/mecha_engine_generation_contract_gate.md`
- `research/package_specs/mecha_engine_contract_traceability_matrix.md`
- `research/package_specs/mecha_engine_property_negative_test_strategy.md`
- `labs/grid_genome/constrained_generator.py`
- `labs/grid_genome/slip.py`
- `packages/mecha_engine/src/mecha_engine/generation/`
- `packages/mecha_engine/tests/test_generation_contract.py`
- `labs/grid_genome/test_package_generation_parity.py`
- `research/experiment_reports/2026-07-04-mecha-engine-genome-promotion.md`
