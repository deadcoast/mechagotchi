# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

Mechagotchi is a **research-first** workspace for a grid-based artificial-life companion engine. There is intentionally **no `packages/` directory yet** — all code lives in `labs/` as executable research prototypes, and the documentation under `research/` *is* the deliverable: a living evidence ledger where every claim traces from the research plan down through experiment reports to lab code and JSON data artifacts.

The governing document is `docs/02-research_plan.md` (thesis, math/ALife layers, Stages 0–7, evaluation framework). `research/README.md` is the master traceability ledger. `_MOC_.md` defines the numeric filename-prefix categories used in `docs/` (`01-` brainstorm/notes → `02-` research plan → `03-` reports → `04-` sources).

## Commands

Lab modules and tests anchor all `data/`/`research/` paths on the repo root via `ROOT = Path(__file__).resolve().parents[2]`, so suites and module `main()`s work from any cwd (review finding L-08). Keep new code on that pattern — and record path *strings* in artifacts repo-relative (`path.relative_to(ROOT).as_posix()`), never absolute.

```powershell
# Run one lab's test suite (stdlib unittest — no pytest, no config files)
python -B -m unittest discover -s labs/grid_genome -p "test_*.py"

# Run a single test file
python -B -m unittest discover -s labs/grid_genome -p "test_validator.py"

# Run a single test method (flat imports — cd into the lab dir first, or add it to sys.path)
python -B -m unittest test_validator.GridValidatorTests.test_valid_grid_passes_core_invariants

# Type check (ad-hoc; no mypy config, no plugins)
python -m mypy labs/<lab>

# Regenerate a lab's data artifacts (each lab has argparse defaults pointing into data/)
python labs/grid_genome/corpus_builder.py
python labs/workshop_editor/png_apng_sidecar_decoder.py

# Validate a changed JSON artifact
python -m json.tool data\<path>\artifact.json
```

**Interpreter caveat:** labs are stdlib-only by convention, with the declared exceptions in `pyproject.toml`'s `lab` dependency group (`pydantic`, `jsonschema` — decision record 0005; provision with `uv sync --group lab`). The `labs/slip_validator/` pydantic/jsonschema labs need those installed; their tests skip (jsonschema) or fail at import (pydantic) without them. Note that `python` in a plain shell may resolve to the system 3.14, and user site-packages (`AppData\Roaming\Python\Python314`) leak into it — the dependency-gate labs *record* module availability (`jsonschema_available` etc.) as per-run observations; never write tests that pin those observations (see review finding H-01). The *package* dependency policy (a `[project]` dependencies list backing `packages/`) is deliberately still blocked.

## Architecture

Data flow: **SLIP profile → grid generator → validator → genome → lifecycle → switchboard → mecha_darwin archive → lineage → render packet.**

- **`research/grid_genome/grid_genome.schema.json`** — authoritative JSON Schema for a grid genome (cells, organs, palette, mutation_profile, lineage). `labs/grid_genome/validator.py` enforces the *semantic* invariants JSON Schema can't express (8-connectivity BFS, organ↔cell reference integrity, required animation anchor). The numbered hard/soft invariants are documented in `research/grid_genome/grid_invariants.md` and referenced by number.
- **SLIP** (Synthetic Learning Intelligence Profile) — a user-authored constraint profile (palettes, body mass bounds, required organ roles, mutation caps, behavior/survival weights) that governs generation. Schema: `research/slip/slip.schema.json`; validated by both stdlib code (`labs/grid_genome/slip.py`, `labs/slip_validator/slip_validator.py`) and a pydantic mirror (`labs/slip_validator/pydantic_contract.py`, which also *generates* `research/slip/slip_pydantic_model.schema.json`). Fixtures: `data/slips/valid/`, `data/slips/failure_cases/`.
- **`labs/`** — each subdirectory is one research lab (grid_genome, workshop_editor, cellular_automata, map_elites_archive, lifecycle_sim, asset_pipeline, readability_benchmark, architecture, package_promotion, …). `labs/workshop_editor/` is the largest: ~30 modules that each isolate one corner of the PNG/APNG/Aseprite/spritesheet spec, hand-encoding and decoding binary formats with only stdlib `struct` + `zlib`, and binding image assets to semantic grids via external metadata sidecars.
- **`data/`** — JSON evidence artifacts and fixture corpora (`data/seed_grids/mg_seed_NNN.json`, `data/invalid_grids/`, per-lab `*_stage0.json` reports).

### Lab module pattern

Every lab module follows the same idiom — preserve it when adding code:

1. `foo.py` with a sibling `test_foo.py` in the same directory. Tests import flat (`from validator import validate_grid`); cross-lab imports mutate `sys.path` at module top. Tests are deterministic and use `tempfile.TemporaryDirectory` for I/O.
2. A `build_*_report(...)` / `run_*_lab(...)` returns a report dict with `artifact_id`, `status`, `date`, `purpose`, `source_artifacts`, metrics, `closed_states`, `blocked_states`, `decision`, `next_research_step`. Keep blocked states explicit — never silently drop an unproven surface.
3. A `write_*_artifacts(output_dir, report)` emits `data/<lab>/<slug>_stage0.json` (sometimes plus binary payloads, a folder README.md, and a `window.MECHAGOTCHI_<X> = {...};` `_data.js` for the workshop UI), guarded by `if __name__ == "__main__":` with argparse defaults into `data/`.
4. Code style: modern union syntax (`str | Path`), `@dataclass(frozen=True)` result types, explicit annotations, stdlib-only unless there is a strong reason.

## Document development format — living files

Documents are living files: **every code or data change must update the corresponding research documents in the same edit.** No algorithm graduates into a future `packages/` directory until it has an algorithm card, an experiment report, a metric report, and a decision record (`research/README.md`).

### The triad convention

Each research finding exists as linked files sharing one slug, differing only by directory and suffix:

```text
research/experiment_reports/2026-05-12-ca-nca-growth-repair.md   ← dated report (YYYY-MM-DD-kebab-slug.md)
research/algorithm_cards/ca_nca_growth_repair.md                 ← card (snake_case, same stem)
labs/cellular_automata/ca_nca_growth_repair.py (+ test_*.py)     ← code
data/cellular_automata/ca_nca_growth_repair_stage0.json          ← evidence
```

`research/README.md` ledgers these triads together, grouped by report version. When adding a lab, create all four surfaces and register them in the ledger.

### Referencing conventions

- **`## Sources` footer**: every research document ends with a list of relative repo paths — the traceability spine. Add/update it whenever a doc's dependencies change.
- **Verification blocks**: experiment reports embed the exact reproducible RED/GREEN/Lab PowerShell commands with pasted output (the unittest discover command that failed, the same command passing, and the lab invocation that produced the artifact).
- **Manifests**: consolidated reports in `research/reports/` (`research_report_v0_N.md`) each have a `*_manifest.json` with `source_plan`, `referenced_artifacts`, and `headline_metrics`. Consolidated reports must not replace the underlying lab reports.
- **Traceability matrices**: `research/package_specs/mecha_engine_contract_traceability_matrix.md` maps Surface → Source Gate → Future Package Test → Required Assertions.
- **IDs**: there is no `RQ-*`/`REQ-*` tag scheme. Research questions are numbered lists grouped by stage in `research/questions.md`; invariants are numbered hard/soft lists in `research/grid_genome/grid_invariants.md`; both are referenced by name/number. Bracket refs `[1]`–`[18]` in the research plan are citation footnotes, not requirement IDs.
- **Algorithm cards** use a fixed template: Name / Purpose / Mathematical basis / Inputs / Outputs / Strengths / Weaknesses / Failure modes / Integration risk / License status / Prototype result / Decision (reject/watch/prototype/adopt) / Go-No-Go gate.
- **Decision records** in `research/decision_records/` are ADR-style, numbered `NNNN-<slug>.md`.
- Long docs use the `vscode-markdown-toc` decimal-numbered TOC with `<a name='...'></a>` anchors. `.markdownlint.json` deliberately disables MD013 (line length), MD024 (duplicate headings — the plan repeats WHY/WHAT/HOW), MD033 (inline HTML), and related rules.

### Completion checklist (before claiming any change done)

1. Run the changed lab's tests: `python -B -m unittest discover -s labs/<lab> -p "test_*.py"`.
2. Validate changed JSON artifacts with `python -m json.tool`.
3. Update the triad documents (experiment report, algorithm card, `research/README.md` ledger entry, `## Sources` footers) in the same change.
4. Do a targeted stale-text search over `research/`, `data/`, and `labs/` for outdated blocker/status wording — `blocked_states` and `closed_states` in prose must match the current artifacts.
