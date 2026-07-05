# Package Specs

This folder holds research-stage package interface specifications. These files
define future package contracts and promotion gates before code is moved from
`labs/` into `packages/`.

Published specs:

- `mecha_engine_module_interfaces.md` - first module interface specs for
  `genome`, `generation`, `lifecycle`, `archive`, and `provenance`.
- `../decision_records/0004-mecha-engine-package-scaffold.md` - accepted
  scaffold shape for the future `packages/mecha_engine` package root.
- `mecha_engine_scaffold_verification_gate.md` - acceptance gate for the future
  empty `src/mecha_engine` scaffold and import-surface tests.
- `mecha_engine_genome_contract_gate.md` - acceptance gate for the future
  `mecha_engine.genome` package contract and validator import surface.
- `mecha_engine_generation_contract_gate.md` - acceptance gate for the future
  `mecha_engine.generation` package contract and constrained generator surface.
- `mecha_engine_lifecycle_contract_gate.md` - acceptance gate for the future
  `mecha_engine.lifecycle` package contract and bounded simulator surface.
- `mecha_engine_archive_contract_gate.md` - acceptance gate for the future
  `mecha_engine.archive` package contract and MAP-Elites archive surface.
- `mecha_engine_provenance_contract_gate.md` - acceptance gate for the future
  `mecha_engine.provenance` package contract and provenance CI surface.
- `mecha_engine_contract_traceability_matrix.md` - matrix that maps scaffold
  and module gates to future package test obligations.
- `mecha_engine_test_fixture_manifest.md` - inventory of concrete repository
  fixtures required by the future package test obligations.
- `mecha_engine_formal_invariant_dependency_gate.md` - cross-module invariant,
  dependency, and failure-propagation gate for future package implementation.
- `mecha_engine_runtime_boundary_gate.md` - package/runtime lifecycle boundary
  gate that keeps SLIP runtime-selection and multigeneration lineage labs
  research-only until package imports and manual readability calibration exist.
- `mecha_engine_property_negative_test_strategy.md` - future property-style,
  metamorphic, and single-fault negative test strategy for package gates.
- `mecha_engine_repair_interface_spec.md` - interface spec for the future
  `mecha_engine.repair` module: wound-site observability contract (damage
  events report destroyed positions, never tokens, never a template),
  validity-guard semantics, and hard gates from the trained-repair
  benchmark. Design-only; the repair package target stays
  decision-record-gated.
