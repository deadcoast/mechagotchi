# mecha_engine Provenance Module Promotion

Date: 2026-07-04

Status: `package_provenance_module_promoted_contract_evidence`

## Purpose

Execute the fifth and final initial-module promotion into
`packages/mecha_engine`, per the traceability matrix order (genome →
generation → lifecycle → archive → **provenance**), against
`research/package_specs/mecha_engine_module_interfaces.md` and
`research/package_specs/mecha_engine_provenance_contract_gate.md`.

## What changed

`packages/mecha_engine/src/mecha_engine/provenance/` implements the full
contracted surface, self-contained (stdlib only, no `labs` imports, no
dependency on any other `mecha_engine` module — the interface spec scopes
provenance inputs to ledgers, included paths, SPDX expressions, and
decision-record references — no artifact writes, typed):

- `spdx.py` — `parse_spdx_expression`: verbatim semantic port of the
  Stage 0 recursive-descent parser: the project-supported identifier
  subset, `LicenseRef-*` and `DocumentRef-...:LicenseRef-*`, `AND` / `OR`
  / `WITH` / `+` / parentheses, sorted `license_ids` / `exception_ids` /
  `operators`, `contains_copyleft` over the known copyleft/share-alike
  set, and structured errors for unknown identifiers, unknown exceptions,
  malformed parentheses, unexpected tokens, and invalid characters.
  Lowercase operators stay rejected under the Stage 0 case-sensitive
  policy; accepting SPDX 3.x lowercase forms requires an explicit schema
  and test revision, not parser drift.
- `hashing.py` — `hash_included_path` (accepts `str | Path`): `sha256`
  for files, deterministic `sha256-tree` for directories (relative POSIX
  path names and child file digests folded in sorted relative-path
  order), `FileNotFoundError` for absent paths, no network access, no
  environment-dependent metadata. Because only paths relative to the
  hashed root enter the digest, results are repo-location independent;
  callers anchor the ledger's repo-relative `included_path` strings on an
  explicit `repo_root` (the post-L-08 anchoring convention).
- `ledger.py` — `validate_ledger(ledger, repo_root)`: verbatim policy
  gate with identical error/warning strings: pinned ledger version
  `0.1.0`, the full `research/asset_provenance/ledger.schema.md` field
  roster, unique `asset_id`s, review-status and SPDX policy (`spdx_id`
  supported and present in `spdx_expression`), included-path existence
  plus hash-algorithm and hash match against committed contents,
  included-asset review policy (`approved`/`needs_legal_review`; included
  external assets must be `approved`), the noncommercial-core rejection,
  the share-alike/copyleft decision-record gate, the attribution-text
  requirement, and JSON-serializable
  `ok`/`errors`/`warnings`/`summary`.
- `report.py` — `build_ci_report` / `generate_attribution_manifest`:
  identical report and manifest shapes (four contracted checks, SPDX
  summary and per-asset results; attribution manifest restricted to
  `attribution_required` assets with the ten preserved fields), pinned
  `0.1.0` versions until a schema migration gate exists. `build_ci_report`
  intentionally hides the lab-only name `build_provenance_ci_report`;
  ledger authoring (`build_stage0_ledger`) and Stage 0 artifact writing
  (`write_stage0_artifacts`) stay lab-only surfaces.

Package tests (`test_provenance_contract.py`, 40 tests, same subprocess
mechanics as genome/generation/lifecycle/archive) prove the contract
gate: the SPDX acceptance set (single IDs, `+`, license refs, document
refs, compound operator expressions) with exact
ids/exceptions/operators/copyleft oracles and the rejection set (unknown
license/exception IDs, all three lowercase operators, malformed
parentheses, dangling/leading operators, empty and non-string
expressions, invalid characters, compound WITH left operands); file and
tree hashing pinned to the committed Stage 0 ledger hashes plus an
independent digest-composition oracle and tempfile property probes
(rename/content/nesting sensitivity, creation-order independence, empty
directory, absent-path `FileNotFoundError`, `str`/`Path` equivalence);
clean validation of the committed ledger reproducing
`validation_report.json` with the 7/3/4/3 Stage 0 summary; a 23-fault
single-fault ledger corpus (P6) each failing for its intended reason
family, the two warning-only excluded-asset anomalies, and the two
positive controls (decision-record metadata clears the share-alike gate;
an approved, correctly-hashed included external asset passes); CI-report
shape and the Stage 0 clean checks byte-reproducing
`provenance_ci_report.json`, with stale-hash, missing-decision-record,
and lowercase-operator faults flipping exactly `included_hashes_ok`,
`decision_record_gate_ok`, and `spdx_expressions_ok`; attribution
manifest generation byte-reproducing `attribution_manifest.json` with
reference-only assets excluded from shipped paths; and purity throughout
(determinism, JSON round-trips, zero input mutation, zero repository
writes — the driver re-digests the five committed `data/asset_provenance`
artifacts before and after all probes).

Lab-side parity
(`labs/asset_pipeline/test_package_provenance_parity.py`, 9 tests) pins
the package against the authoritative research lab: the lab-rebuilt
Stage 0 ledger equals the committed `ledger.json`; package
validation/CI-report/attribution outputs equal the lab outputs and
re-derive the committed `validation_report.json`,
`provenance_ci_report.json`, and `attribution_manifest.json`
byte-identically (`json.dumps(..., indent=2) + "\n"`); all three included
paths hash identically through both surfaces to the committed
hash/algorithm pairs; SPDX parsing is dict-identical across all seven
ledger expressions and a 25-expression accept/reject mutation corpus; and
16 fault-injected ledgers plus three fault-injected CI reports produce
identical outputs error-for-error.

Documented spec resolutions: `hash_included_path` and the `repo_root`
parameters accept `str | Path` (the lab type-hints `Path`; the contract
signatures say `path` / `repo_root` untyped). The `sha256-tree` child
order is the Stage 0 reference sort (Python path ordering), pinned by the
committed seed-grid corpus hash — the contract-gate wording
"deterministic relative-path order" is restated in the driver oracle as
composition (relative POSIX names + child digests) with the pinned sort.
The lab's `share-alike asset cannot be core without decision record`
check fires on `share_alike_required` core assets regardless of a
decision record (the decision record clears only the
`requires decision_record` error); the package replicates this verbatim
rather than "fixing" it — relaxing it would need a schema revision. The
Stage 0 fallback `generated_date` (`2026-05-12`) for ledgers without one
is kept for verbatim parity. The interface spec's "Provenance Result"
field list (`ok`, `checks`, `parsed_expressions`, `included_hashes`,
`decision_record_gate`, `errors`) is satisfied through the contract
gate's concrete CI-report shape (`checks` carries the four gates,
`spdx_results`/`spdx_summary` carry parsed expressions, hash and
decision-record outcomes surface in `checks` + `errors`), which the gate
document makes authoritative.

## Result

- Stage 0 provenance artifacts reproduced exactly through the package
  surface: validation ok with 7 assets / 3 included / 4 reference-only /
  3 attribution-required, CI report ok with 7/7 expressions parsed and
  all four checks true, attribution manifest with the three
  reference-only external tools — all three committed JSON artifacts
  re-derived byte-identically by both the package tests and the lab-side
  parity suite.
- Committed included hashes verified against committed contents: the
  seed-grid corpus `sha256-tree` and both file `sha256` hashes match
  through `hash_included_path`, and stale/missing/mismatched-algorithm
  hashes fail validation and flip `included_hashes_ok`.
- SPDX strictness preserved: unknown license and exception identifiers,
  lowercase `and`/`or`/`with`, malformed parentheses, and invalid tokens
  all reject; parsing is deterministic with sorted outputs.
- Decision-record policy enforced: included share-alike/copyleft assets
  without `decision_record` fail and flip `decision_record_gate_ok`;
  supplying the record clears the gate; share-alike core assets stay
  rejected; reference-only assets stay excluded from shipped paths while
  keeping attribution.
- No writes and no input mutation anywhere in the surface; the gate stays
  described as a research/package-promotion policy gate, not legal review
  or REUSE compliance; release license metadata stays blocked.
- Boundary scan over `packages/mecha_engine`: zero matches.

```powershell
python -B -m unittest discover -s packages/mecha_engine/tests -p "test_*.py"
# Ran 163 tests - OK  (was 123; +40 provenance contract)
```

Scaffold verification gate: `promoted_modules` now
`["genome", "generation", "lifecycle", "archive", "provenance"]` —
all five initial modules promoted, `unpromoted_modules` empty — 9/9
checks pass, artifact regenerated. The gate keeps its single
promoted-modules decision string
(`accept_package_scaffold_with_promoted_modules`, status
`package_scaffold_verification_executed_promoted_modules_present`); it
defines no distinct all-promoted decision, so its `next_research_step`
renders with an empty unpromoted list. The architecture lab's gate test
was updated to pin the five-module state. Full 12-lab sweep: 520 lab
tests (was 511; +9 provenance parity) + 163 package tests, all green.
The package-promotion gate rerun (`data/package_promotion`) is deferred
to the orchestrated promotion-gate step and not rerun here.

## Decision

`mecha_engine.provenance` is promoted with contract evidence, completing
the five initial modules of the traceability order. Repository-wide REUSE
scanning, `REUSE.toml` generation, legal review, package license
metadata, full SPDX License List ingestion, SBOM generation, and the
SPDX 3.x lowercase-operator policy all remain deferred per the contract
gate. Next step in the promotion sequence: the orchestrated
package-promotion gate rerun over the completed five-module surface.

## Verification

```powershell
python -B -m unittest discover -s packages/mecha_engine/tests -p "test_*.py"
python -B -m unittest discover -s labs/asset_pipeline -p "test_*.py"
python -B labs/asset_pipeline/test_package_provenance_parity.py
python -B -m unittest discover -s labs/architecture -p "test_*.py"
python -B labs/architecture/mecha_engine_scaffold_verification_gate.py
python -m json.tool data/architecture/mecha_engine_scaffold_verification_gate_stage0.json
```

## Sources

- `research/package_specs/mecha_engine_module_interfaces.md`
- `research/package_specs/mecha_engine_provenance_contract_gate.md`
- `research/package_specs/mecha_engine_contract_traceability_matrix.md`
- `research/package_specs/mecha_engine_property_negative_test_strategy.md`
- `research/asset_provenance/ledger.schema.md`
- `data/architecture/mecha_engine_provenance_contract_gate_stage0.json`
- `data/asset_provenance/ledger.json`
- `data/asset_provenance/validation_report.json`
- `data/asset_provenance/provenance_ci_report.json`
- `data/asset_provenance/attribution_manifest.json`
- `labs/asset_pipeline/provenance_ledger.py`
- `packages/mecha_engine/src/mecha_engine/provenance/`
- `packages/mecha_engine/tests/test_provenance_contract.py`
- `labs/asset_pipeline/test_package_provenance_parity.py`
- `research/experiment_reports/2026-07-04-mecha-engine-archive-promotion.md`
