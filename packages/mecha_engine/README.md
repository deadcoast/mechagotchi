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

Deferred modules (must not exist until their own decision records and gates
clear): `learning`, `render`, `storage`, `slip`.

Release license metadata is deliberately unset in `pyproject.toml` until the
repository/package license decision is explicit. The package is stdlib-only;
the package dependency policy remains blocked.

## Tests

```powershell
python -B -m unittest discover -s .\packages\mecha_engine\tests -p "test_*.py"
```

The tests exercise `mecha_engine` in subprocesses against the `src/` layout
(or the installed package, per the verification gate's documented
`python -m pip install -e .\packages\mecha_engine` flow); they never import
research lab modules, and no `sys.path` text exists anywhere in the package
tree.
