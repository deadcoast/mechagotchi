# mecha-engine

Mechagotchi engine core package (import package `mecha_engine`,
distribution package `mecha-engine`). The scaffold boundary was created per
decision record `research/decision_records/0004-mecha-engine-package-scaffold.md`;
implementation arrives module-by-module only after the corresponding
contract/promotion gate passes: the package-promotion gate lab
(`package_promotion_gate.py` in the research lab tree),
`research/package_specs/mecha_engine_scaffold_verification_gate.md`, and the
per-module contract gates under `research/package_specs/`.

Promoted modules (each with package contract tests and a lab-side parity
pin):

- `mecha_engine.genome` (2026-07-04)
- `mecha_engine.generation` (2026-07-04)
- `mecha_engine.lifecycle` (2026-07-04)
- `mecha_engine.archive` (2026-07-04)
- `mecha_engine.provenance` (2026-07-04)
- `mecha_engine.repair` (2026-07-05, decision record 0006 — wound-site
  learned repair; observability contract: damage events report destroyed
  positions, never destroyed tokens, never a template)
- `mecha_engine.runtime` (2026-07-05, decision record 0008 — the composed
  engine's entry point: `live_cycle` + `evolve`; SLIP-aware repair
  throughout, readability injected and visibly uncalibrated)
- `mecha_engine.learning` (2026-07-05, decision record 0009 — the feedback
  micro-switchboard; bounded claim: need-balance improvement at zero
  survival cost — survival is morphology-decided, no survival claim)

- `mecha_engine.storage` (decision record 0022: transactional campaign ledger;
  stored engine reports remain authoritative)
- `mecha_engine.slip` (decision record 0027: public covenant validation/alignment)

`render` remains deferred; native rendering belongs to the separate game client.
The declared license is Apache-2.0 (decision record 0028 and `pyproject.toml`).
The package currently declares no third-party dependencies. The dependency policy
permits a justified, declared addition through its own decision record; it is not
a blanket dependency ban or a publication approval.

## Seeded public example

Use the provisioned repository environment or an installed `mecha-engine` package:

```powershell
.venv/Scripts/python.exe -B -m mecha_engine.runtime.examples.seeded --output NEW_ENGINE_OUTPUT --rng-seed 20261006
```

The output directory must be new. Existing paths are refused without overwriting
their contents. The example authors an 8x8 toy seed and covenant, trains small
explicit models, and calls promoted validation/generation/repair/runtime/archive
APIs. It writes the exact seed, covenant, elites and engine report into that new
directory. It does not read or regenerate historical Stage0 research evidence.

Readability is an explicitly uncalibrated constant (0.5). Training/evolution budgets
are teaching settings, not calibration or performance evidence. Empty archives
and extinction remain actual engine outcomes. No default policy is promoted.
The example lives under the already promoted runtime boundary and introduces no
new algorithm authority or lab import.

## Tests

```powershell
python -B -m unittest discover -s .\packages\mecha_engine\tests -p "test_*.py"
```

The tests exercise `mecha_engine` in subprocesses against the `src/` layout
(or the installed package, per the verification gate's documented
`python -m pip install -e .\packages\mecha_engine` flow); they never import
research lab modules, and no `sys.path` text exists anywhere in the package
tree.


## Immutable era execution evidence (DR0084)

The storage writer uses additive schema 2; read-only consumers accept schemas 1 and 2
without migration. Existing reports, elite JSON text and replay hashes are preserved.
`record_era(..., execution=None)` optionally commits immutable byte-addressed blobs,
an execution manifest and ordered founder occurrences in the same era transaction.
`validate_execution(bundle)` checks structure and byte references without I/O;
`load_era_execution(conn, campaign_id, era_index)` verifies stored identity, results
and occurrence projections. Historical missing evidence returns `None`.

A digest cannot acquire different bytes or media. Contradictory admission streams
and ordered elite payloads refuse on write and read; retries do not replace evidence.
The engine observer is `evolve(..., admission_callback=None)` and emits isolated
actual decisions by occurrence. Reproduction is a game consumer of retained inputs,
not an engine default or a scientific-policy promotion. See the preregistered
`docs/development/cycle-38-immutable-era-inputs.md` and measured
`research/experiment_reports/2026-10-06-reproducible-era-inputs.md` for closing gates.
