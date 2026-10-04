# A source-informed, resumable local development cycle

Date: 2026-10-04. Decision: DR 0062. Baseline: `7a48886`.

## WHY

CI repair alone does not give the next active agent a reliable operating loop.
The repository already supplies the product queue and scientific gates. This
slice makes execution, workspace identity, validation and resumption concrete
without claiming an unattended model is running or inventing a new backlog.

## WHAT

The repair was first integrated into the requested local repository and
reverified there (390 focused tests, no tracked-byte changes). This workflow
was then preregistered and implemented in that actual folder. `mechas develop`
records phase/checkpoints, preserves a completed cycle, selects known focused
suites or the full sweep, retains output, and rejects changed/stale/incomplete
evidence. Root, branch and HEAD accompany state so directory substitution is
visible. Q2 is preregistered from its real validator/lifecycle/session seams.

## FINDINGS

The first complete focused workflow run passed 37 tests without changing source.
Review then exposed a subtler invalidation bug: an old full pass could become
current again after a later failed focused run was repaired. A new regression
failed before the correction. Verification now considers only results after
the most recent failure; focused recovery cannot resurrect that old full pass.

The final instrument also refuses missing dependencies and incomplete full
suite sets, and terminates its own subprocess tree on timeout/interruption
while retaining partial output. Tests use real subprocesses and temporary Git
repositories, not mocks that merely restate the implementation.

Remote publishing remains blocked by execution approval. Native Windows and
Ubuntu Actions have not verified this local commit. The workflow reports this
gate as unmet on every status; local checks cannot change it.

## Verification

Specifications and the initial regression suite preceded implementation:

```powershell
& $py -B -m unittest discover -s tools/mechas_cli/tests -p test_development.py
Ran 1 test in 0.000s
FAILED (errors=1)
# ImportError: cannot import name 'development' from 'mechas_cli'

# First focused GREEN, then review-driven regression RED:
& $py -B -m unittest discover -s tools/mechas_cli/tests -p test_development.py -v
Ran 7 tests in 20.431s
OK
& $py -B -m unittest test_development.DevelopmentCycleTests.test_failure_revokes_earlier_full_result_even_after_focused_recovery
Ran 1 test in 3.329s
FAILED (failures=1)
# AssertionError: True is not false
```

The single-method RED command runs from `tools/mechas_cli/tests`. `$py` is an
explicitly provisioned Python 3.14.3 interpreter with all locked dependency
groups. The operational CLI takes the same interpreter through `--python`.

Final focused verification: 39 tests passed (CLI 35, CI instrument 4),
including all 11 workflow regressions. No inventoried source bytes changed.

```powershell
$env:PYTHONPATH = (Resolve-Path tools/mechas_cli/src).Path
& $py -B -m mechas_cli.app develop --verify full --python $py
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
cli: PASSED, 35 tests, 0 skipped
game: PASSED, 239 tests, 0 skipped
workshop: PASSED, 92 tests, 0 skipped
ci: PASSED, 4 tests, 0 skipped
2260 JSON artifacts valid
SWEEP GREEN
Workflow result: passed=true, tests_run=2453, changed_files=[]
```

Actual full run: `20261004T073038-9e53e79e` in the requested repository.
Summary: `.development/runs/20261004T073038-9e53e79e/summary.json`; the sibling `result.json` records
the command, full inventory, source fingerprint and return code. Logs are
local runtime evidence, deliberately ignored by Git. The committed metric
artifact records the final focused instrument run; this report records the
subsequent full sweep. A documentation-only result update follows the run.
The local phase transition and Q2 review checkpoint are retained in state
and completed-cycle history. Remote acceptance remains unverified.

## Installed command smoke check

The existing `mechas.exe` entry point failed with
`ModuleNotFoundError: No module named 'mechas_cli'`. Its editable installation
was relinked to the requested repository, offline, using the existing lock's
CLI dependency versions and Python 3.14.3. No source dependency changed.
`mechas develop --status` now runs directly and reports the requested root,
`phase=polish`, `full_current=true`, `local_complete=true`, and the publication
gate still `unmet`. The source invocation remains available as a fallback.

## Scope and next checkpoint

The local operating slice is distinct from Q2 feature implementation. Q2's
mechanics shape, version rules, explicit-empty override precedence, persistence
requirements and corpus-change accounting are preregistered. Q2 remains open
in the live queue until its own implementation and evidence pass. Q3-Q5 and
Q1's separate promotion gate retain their existing meanings.

## Sources

- `docs/development/local-cycle.md`, `docs/development/workflow.json`
- `docs/development/q2-mechanics-rung.md`, `AGENTS.md`, `sunsetted/TODO.md`
- `research/decision_records/0062-local-development-cycle.md`
- `research/algorithm_cards/local_development_cycle.md`
- `data/development/local_development_cycle_stage0.json`
- `tools/mechas_cli/src/mechas_cli/development.py`
- `tools/mechas_cli/tests/test_development.py`, `tools/ci/tests/test_run_sweep.py`
