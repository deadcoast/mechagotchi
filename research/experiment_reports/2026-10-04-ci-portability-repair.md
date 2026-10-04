# CI portability repair: two root failures, one obscuring instrument

Date: 2026-10-04. Decision: DR 0061. Baseline: `19cc73d`.

## WHY

GitHub sweep #32 fails on both operating systems despite the committed local
green claim. Run #27 has the same signature, so Q1 is not the onset. The failing
suites are architecture (1), asset_pipeline (Windows 4 / Ubuntu 6),
runtime_integration (1), package (9 / 10), and CLI (4). Game and workshop pass;
2,254 artifacts parse. Parsing JSON does not validate provenance.

## WHAT

The review used isolated snapshots and retained full subprocess output. The
original worktree remained clean. CRLF and LF snapshots reproduced the observed
provenance failure counts. Native Linux was not available locally; the Linux
claim is reserved for GitHub's native job on the final commit.

The repair pins LF checkout bytes for hashed assets, defines case-sensitive
relative POSIX-string tree ordering in both implementations, preserves the
four original provenance blobs, and records the current baseline's new date,
policy and all digest deltas. It decodes ANSI for CLI semantic assertions,
retains sweep diagnostics and isolates three SLIP writer tests from committed
artifacts. The implementation specification was written before implementation.

## FINDINGS

The original Windows seed tree hash `65ba5924...` describes CRLF JSON plus an
LF README. A fresh Windows-style checkout changes only that README and hashes
to `34d75023...`. Linux also changes the two standalone included files to LF.
Native Path sorting additionally changes directory order across platforms.
The corrected tree digest is `7b2f0571...`; complete values are in the
restatement artifact. Corpus JSON values are unchanged.

Architecture's `package_import_test_suite_passes` and runtime's
`provenance.ledger_ok` are downstream of the same digest failures. Package
negative controls that expect unrelated checks to stay green fail for this
same reason; their conditions have not been weakened.

CLI help succeeds but its bold option text contains ANSI boundaries between
characters. `NO_COLOR` does not remove styles. The unchanged baseline passes
23 CLI tests under TERM=dumb and fails exactly the four help tests under
GITHUB_ACTIONS=true / TERM=xterm-256color. Decoding ANSI preserves the option
contract, and the new subprocess regression runs both terminal modes.

The old sweep retained only the final subprocess-output line; historical
tracebacks were therefore unavailable. The new runner retains separate logs,
counts, return codes, timeouts and environment observations with an incremental
summary. Empty discovery cannot masquerade as a green suite.

## Verification

Baseline and regression RED runs used the existing Python 3.13.9 environment;
focused GREEN also used that environment. The full sweep uses an isolated
Python 3.14.3 venv provisioned from the unchanged lock, including all groups.

```powershell
# New portability pin before implementation
& $py -B -m unittest discover -s labs/asset_pipeline -p test_provenance_portability.py
Ran 1 test in 0.011s
FAILED (failures=1)

# New diagnostic pins before implementation
& $py -B -m unittest discover -s tools/ci/tests -p test_run_sweep.py
Ran 3 tests in 0.007s
FAILED (errors=3)

# Focused GREEN; identical discovery commands, expanded to each full suite
& $py -B -m unittest discover -s labs/asset_pipeline -p 'test_*.py'
Ran 23 tests in 0.347s
OK
& $py -B -m unittest discover -s packages/mecha_engine/tests -p 'test_*.py'
Ran 316 tests in 7.853s
OK
& $py -B -m unittest discover -s labs/slip_validator -p 'test_*.py'
Ran 24 tests in 0.229s
OK
& $py -B -m unittest discover -s tools/mechas_cli/tests -p 'test_*.py'
Ran 24 tests in 6.265s
OK
& $py -B -m unittest discover -s tools/ci/tests -p 'test_*.py'
Ran 3 tests in 1.267s
OK
```

Process disclosure: portability and runner pins were RED first. The CLI RED
was the baseline environment reproduction. Output-isolation assertions were
added with the writer changes, not claimed as a separate recorded RED run.

```powershell
& .\.venv\Scripts\python.exe -B tools/ci/run_sweep.py
lab:animation_system: PASSED, 38 tests, 0 skipped
lab:architecture: PASSED, 76 tests, 0 skipped
lab:asset_pipeline: PASSED, 23 tests, 0 skipped
lab:cellular_automata: PASSED, 53 tests, 0 skipped
lab:ctm_ticks: PASSED, 4 tests, 0 skipped
lab:cubff_transducer: PASSED, 58 tests, 0 skipped
lab:datasets: PASSED, 22 tests, 0 skipped
lab:game_loop: PASSED, 84 tests, 0 skipped
lab:grid_genome: PASSED, 226 tests, 0 skipped
lab:lifecycle_sim: PASSED, 43 tests, 0 skipped
lab:map_elites_archive: PASSED, 464 tests, 0 skipped
lab:micro_threads: PASSED, 160 tests, 0 skipped
lab:package_promotion: PASSED, 6 tests, 0 skipped
lab:readability_benchmark: PASSED, 42 tests, 0 skipped
lab:repair_boundary: PASSED, 4 tests, 0 skipped
lab:runtime_integration: PASSED, 65 tests, 0 skipped
lab:slip_validator: PASSED, 24 tests, 0 skipped
lab:wfc_grid: PASSED, 61 tests, 0 skipped
lab:workshop_editor: PASSED, 314 tests, 0 skipped
package: PASSED, 316 tests, 0 skipped
cli: PASSED, 24 tests, 0 skipped
game: PASSED, 239 tests, 0 skipped
workshop: PASSED, 92 tests, 0 skipped
ci: PASSED, 3 tests, 0 skipped
2259 JSON artifacts valid
SWEEP GREEN
```

All 24 suites passed. A raw-byte audit of previously tracked files found only
the intentional ONBOARDING.md documentation edit made during the run; no
scientific evidence changed. The staged worktree also had no unstaged changes
after the sweep. Cloud acceptance is the Actions result attached to the
published commit, not inferred from local runs.

## Sources

- `docs/development/ci-reproducibility.md`
- `research/decision_records/0061-portable-provenance-and-ci-evidence.md`
- `data/asset_provenance/portability_restatement_stage0.json`
- `data/asset_provenance/baselines/stage0-windows/`
- `labs/asset_pipeline/provenance_ledger.py`, `labs/asset_pipeline/test_provenance_portability.py`
- `packages/mecha_engine/src/mecha_engine/provenance/hashing.py`
- `tools/mechas_cli/tests/test_cli_surface.py`, `tools/ci/run_sweep.py`
- `labs/slip_validator/test_pydantic_contract.py`, `test_schema_migration_gate.py`, `test_jsonschema_runtime_parity.py`
- https://github.com/deadcoast/mechagotchi/actions/runs/31311673414
- https://github.com/deadcoast/mechagotchi/actions/runs/31299423672
- https://docs.python.org/3/library/pathlib.html#general-properties
- https://git-scm.com/docs/gitattributes
- https://raw.githubusercontent.com/fastapi/typer/0.26.8/typer/rich_utils.py
- https://rich.readthedocs.io/en/latest/console.html#environment-variables
