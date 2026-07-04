# mecha-engine

Empty package scaffold for the Mechagotchi engine core (import package
`mecha_engine`, distribution package `mecha-engine`), created per decision
record `research/decision_records/0004-mecha-engine-package-scaffold.md`.

This scaffold defines the package boundary only. Every module below is an
empty placeholder: no lab implementation was moved or copied during scaffold
creation, and implementation arrives module-by-module only after the
corresponding contract/promotion gate passes: the package-promotion gate lab
(`package_promotion_gate.py` in the research lab tree),
`research/package_specs/mecha_engine_scaffold_verification_gate.md`, and the
per-module contract gates under `research/package_specs/`.

Initial (empty) module boundaries:

- `mecha_engine.genome`
- `mecha_engine.generation`
- `mecha_engine.lifecycle`
- `mecha_engine.archive`
- `mecha_engine.provenance`

Deferred modules (must not exist until the core boundary is verified and
their gates clear): `learning`, `repair`, `render`, `storage`, `slip`.

Release license metadata is deliberately unset in `pyproject.toml` until the
repository/package license decision is explicit.

## Tests

```powershell
python -B -m unittest discover -s .\packages\mecha_engine\tests -p "test_*.py"
```

The import-surface tests exercise `mecha_engine` in subprocesses against the
`src/` layout (or the installed package, per the verification gate's
documented `python -m pip install -e .\packages\mecha_engine` flow); they
never import research lab modules.
